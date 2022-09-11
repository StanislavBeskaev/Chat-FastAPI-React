import asyncio

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from loguru import logger

from backend import models, tables
from backend.dao.chats import ChatsDAO
from backend.dao.messages import MessagesDAO
from backend.dao.users import UsersDAO
from backend.db_config import get_session
from backend.services import BaseService
from backend.services.chat_members import ChatMembersService
from backend.services.ws import NewChatMessage, ChangeChatNameMessage, InfoMessage


class ChatService(BaseService):
    """Сервис для работы с чатами"""

    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session=session)
        self._chat_members_service = ChatMembersService(session=session)

        self._chats_dao = ChatsDAO(session=session)
        self._messages_dao = MessagesDAO(session=session)
        self._users_dao = UsersDAO(session=session)

    def create_chat(self, chat_data: models.ChatCreate, user: models.User) -> None:
        """Создание чата"""
        logger.debug(f"Попытка создания нового чата, {chat_data=} {user=}")
        chat_users = self._validate_new_chat_data(chat_data=chat_data)

        new_chat = self._chats_dao.create_chat(chat_name=chat_data.chat_name, creator_id=user.id)
        for chat_user in chat_users:
            self._chat_members_service.add_user_to_chat(user=chat_user, chat_id=new_chat.id)

        logger.info(f"Пользователь {user.login} создал новый чат {new_chat.name} с id {new_chat.id}")
        self._notify_about_new_chat(new_chat=new_chat, creator=user.login)

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

        chat_users = [self._users_dao.find_user_by_login(login) for login in chat_data.members]
        if not all(chat_users):
            logger.warning("В списке участников есть не существующие пользователи")
            raise HTTPException(status_code=400, detail="В списке участников есть не существующие пользователи")

        chat_users = [models.User.from_orm(user) for user in chat_users]
        logger.debug(f"{chat_users=}")
        return chat_users

    @staticmethod
    def _notify_about_new_chat(new_chat: tables.Chat, creator: str) -> None:
        """ws уведомление участников чата о создании нового чата"""
        new_chat_message = NewChatMessage(chat_id=new_chat.id, chat_name=new_chat.name, creator=creator)
        asyncio.run(new_chat_message.send_all())

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
        previous_chat_name = self._chats_dao.get_chat_by_id(chat_id=chat_id).name
        if previous_chat_name == new_name:
            logger.warning("Передано такое же название чата, изменение названия не выполнятся")
            raise HTTPException(status_code=400, detail="Название чата совпадает с текущим")

        chat = self._chats_dao.change_chat_name(chat_id=chat_id, new_name=new_name)

        logger.info(f"Для чата {chat_id} установлено название: {new_name}")
        change_chat_name_message = self._create_change_chat_name_message(user=user, chat_id=chat_id, new_chat_name=new_name)  # noqa
        self._notify_about_change_chat_name(changed_chat=chat, message=change_chat_name_message, login=user.login)

    def _is_user_chat_creator(self, chat_id: str, user: models.User) -> bool:
        """Является ли пользователь создателем чата"""
        chat = self._chats_dao.get_chat_by_id(chat_id=chat_id)

        return chat.creator_id == user.id

    @staticmethod
    def _notify_about_change_chat_name(changed_chat: models.Chat, message: tables.Message, login: str) -> None:
        """ws уведомление участников чата об изменении названия чата"""
        new_chat_message = ChangeChatNameMessage(chat_id=changed_chat.id, chat_name=changed_chat.name)
        asyncio.run(new_chat_message.send_all())

        ws_info_change_chat_name_message = InfoMessage(login=login, info_message=message)
        asyncio.run(ws_info_change_chat_name_message.send_all())

    def _create_change_chat_name_message(self, user: models.User, chat_id: str, new_chat_name) -> models.Message:
        """Создание сообщения в базе об изменении названия чата"""
        change_chat_name_message = self._messages_dao.create_info_message(
            text=f"Название чата изменено на '{new_chat_name}'",
            user_id=user.id,
            chat_id=chat_id
        )

        logger.info(f"В базу сохранено сообщение об изменении названия чата {chat_id} на '{new_chat_name}'")
        return change_chat_name_message
