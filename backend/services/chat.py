import asyncio

from fastapi import Depends, HTTPException
from loguru import logger

from backend import models, tables
from backend.settings import get_settings
from backend.db.facade import get_db_facade
from backend.db.interface import DBFacadeInterface
from backend.services import BaseService
from backend.services.chat_members import ChatMembersService
from backend.services.ws import NewChatMessage, ChangeChatNameMessage, InfoMessage


class ChatService(BaseService):
    """Сервис для работы с чатами"""

    def __init__(self, db_facade: DBFacadeInterface = Depends(get_db_facade)):
        super().__init__(db_facade=db_facade)
        self._chat_members_service = ChatMembersService(db_facade=db_facade)

    def create_chat(self, chat_data: models.ChatCreate, user: models.User) -> None:
        """Создание чата"""
        logger.debug(f"Попытка создания нового чата, {chat_data=} {user=}")
        chat_users = self._validate_new_chat_data(chat_data=chat_data)

        new_chat = self._db_facade.create_chat(chat_name=chat_data.chat_name, creator_id=user.id)
        for chat_user in chat_users:
            self._chat_members_service.add_user_to_chat(user=chat_user, chat_id=new_chat.id)

        logger.info(f"Пользователь {user.login} создал новый чат {new_chat.name} с id {new_chat.id}")
        self._notify_about_new_chat(new_chat=new_chat, user=user)

    def change_chat_name(self, chat_id: str, new_name: str, user: models.User) -> None:
        """Изменение названия чата"""
        logger.debug(f"Попытка изменить название чата: {chat_id=} {new_name=} {user=}")
        if not self._is_user_chat_creator(chat_id=chat_id, user=user):
            logger.warning("Пользователь не является создателем чата, изменение названия не выполнятся")
            raise HTTPException(
                status_code=403,
                detail="Изменить название чата может только создатель"
            )

        if not new_name:
            logger.warning("Передано пустое новое название, изменение названия не выполнятся")
            raise HTTPException(status_code=400, detail="Укажите название чата")

        # Тут будет 404 если чата нет
        previous_chat_name = self._db_facade.get_chat_by_id(chat_id=chat_id).name
        if previous_chat_name == new_name:
            logger.warning("Передано такое же название чата, изменение названия не выполнятся")
            raise HTTPException(status_code=400, detail="Название чата совпадает с текущим")

        chat = self._db_facade.change_chat_name(chat_id=chat_id, new_name=new_name)

        logger.info(f"Для чата {chat_id} установлено название: {new_name}")
        change_chat_name_message = self._create_change_chat_name_message(user=user, chat_id=chat_id, new_chat_name=new_name)  # noqa
        self._notify_about_change_chat_name(changed_chat=chat, message=change_chat_name_message, login=user.login)

    def try_leave_chat(self, chat_id: str, user: models.User) -> str:
        """Попытка покинуть чат, возвращается сообщение для отображения в модальном окне на front'е"""
        if chat_id == get_settings().main_chat_id:
            raise HTTPException(status_code=403, detail="Нельзя покинуть главный чат")

        # Тут будет 404 если чата нет
        if self._is_user_chat_creator(chat_id=chat_id, user=user):
            return "Вы создатель чата. Это приведёт к удалению чата. Вы уверены?"

        if not self._chat_members_service.is_user_in_chat(user=user, chat_id=chat_id):
            raise HTTPException(status_code=400, detail="Вы не участник чата")

        return "Вы уверены, что хотите покинуть чат?"

    def _validate_new_chat_data(self, chat_data: models.ChatCreate) -> list[models.User]:
        """Проверка данных для создания нового чата"""
        if not chat_data.chat_name:
            logger.warning("Не указано имя чата")
            raise HTTPException(status_code=400, detail="Не указано имя чата")

        if not chat_data.members:
            logger.warning("Не указаны участники чата")
            raise HTTPException(status_code=400, detail="Не указаны участники чата")

        if len(chat_data.members) < 2:
            logger.warning("Необходимо добавить хотя бы ещё одного участника")
            raise HTTPException(status_code=400, detail="Необходимо добавить хотя бы ещё одного участника")

        chat_users = [self._db_facade.find_user_by_login(login) for login in chat_data.members]
        if not all(chat_users):
            logger.warning("В списке участников есть не существующие пользователи")
            raise HTTPException(status_code=400, detail="В списке участников есть не существующие пользователи")

        chat_users = [models.User.from_orm(user) for user in chat_users]
        logger.debug(f"{chat_users=}")
        return chat_users

    def _notify_about_new_chat(self, new_chat: tables.Chat, user: models.User) -> None:
        """ws уведомление участников чата о создании нового чата"""
        new_chat_message = NewChatMessage(
            chat_id=new_chat.id,
            chat_name=new_chat.name,
            creator=user.login,
            db_facade=self._db_facade
        )
        asyncio.run(new_chat_message.send_all())

        new_chat_info_message = self._create_new_chat_info_message(user=user, chat=new_chat)
        ws_info_message = InfoMessage(login=user.login, info_message=new_chat_info_message, db_facade=self._db_facade)
        asyncio.run(ws_info_message.send_all())

    def _is_user_chat_creator(self, chat_id: str, user: models.User) -> bool:
        """Является ли пользователь создателем чата"""
        chat = self._db_facade.get_chat_by_id(chat_id=chat_id)

        return chat.creator_id == user.id

    def _notify_about_change_chat_name(self, changed_chat: models.Chat, message: models.Message, login: str) -> None:
        """ws уведомление участников чата об изменении названия чата"""
        new_chat_message = ChangeChatNameMessage(
            chat_id=changed_chat.id,
            chat_name=changed_chat.name,
            db_facade=self._db_facade
        )
        asyncio.run(new_chat_message.send_all())

        ws_info_change_chat_name_message = InfoMessage(login=login, info_message=message, db_facade=self._db_facade)
        asyncio.run(ws_info_change_chat_name_message.send_all())

    def _create_change_chat_name_message(self, user: models.User, chat_id: str, new_chat_name) -> models.Message:
        """Создание сообщения в базе об изменении названия чата"""
        change_chat_name_message = self._db_facade.create_info_message(
            text=f"Название чата изменено на '{new_chat_name}'",
            user_id=user.id,
            chat_id=chat_id
        )

        logger.info(f"В базу сохранено сообщение об изменении названия чата {chat_id} на '{new_chat_name}'")
        return change_chat_name_message

    def _create_new_chat_info_message(self, user: models.User, chat: models.Chat) -> models.Message:
        """Создание информационного сообщения в базе о создании нового чата"""
        new_chat_info_message = self._db_facade.create_info_message(
            text=f"Пользователь {user.login} создал чат",
            user_id=user.id,
            chat_id=chat.id
        )

        return new_chat_info_message
