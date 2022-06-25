import asyncio
from collections import OrderedDict
from uuid import uuid4

from fastapi import Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session, aliased
from loguru import logger

from backend import models, tables
from backend.database import get_session
from backend.services import BaseService
from backend.services.chat_members import ChatMembersService
from backend.services.user import UserService
from backend.services.ws import NewChatMessage, ChangeChatNameMessage


class MessageService(BaseService):
    """Сервис для работы с сообщениями и чатами"""

    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session=session)
        self._user_service = UserService(session=session)
        self._chat_members_service = ChatMembersService(session=session)

    def create_chat(self, chat_data: models.ChatCreate, user: models.User) -> None:
        """Создание чата"""
        logger.debug(f"Попытка создания нового чата, {chat_data=} {user=}")
        chat_users = self._validate_new_chat_data(chat_data=chat_data)

        new_chat = tables.Chat(
            id=str(uuid4()),
            name=chat_data.chat_name,
            creator_id=user.id
        )
        self.session.add(new_chat)
        self.session.commit()
        for chat_user in chat_users:
            self._chat_members_service.add_user_to_chat(user=chat_user, chat_id=new_chat.id)

        logger.info(f"Пользователь {user.login} создал новый чат {new_chat.name} с id {new_chat.id}")
        self._notify_about_new_chat(new_chat=new_chat, creator=user.login)

    def _validate_new_chat_data(self, chat_data: models.ChatCreate) -> list[models.User]:
        """Проверка данных для создания нового чата"""
        if not chat_data.chat_name:
            logger.error("Не указано имя чата")
            raise HTTPException(status_code=400, detail="Не указано имя чата")

        if not chat_data.members:
            logger.error("Не указаны участники чата")
            raise HTTPException(status_code=400, detail="Не указаны участники чата")

        if len(chat_data.members) < 2:
            logger.error("Необходимо добавить хотя бы ещё одного участника")
            raise HTTPException(status_code=400, detail="Необходимо добавить хотя бы ещё одного участника")

        chat_users = [self._user_service.find_user_by_login(login) for login in chat_data.members]
        if not all(chat_users):
            logger.error("В списке участников есть не существующие пользователи")
            raise HTTPException(status_code=400, detail="В списке участников есть не существующие пользователи")

        chat_users = [models.User.from_orm(user) for user in chat_users]
        logger.debug(f"{chat_users=}")
        return chat_users

    @staticmethod
    def _notify_about_new_chat(new_chat: tables.Chat, creator: str) -> None:
        """ws уведомление участников чата о создании нового чата"""
        new_chat_message = NewChatMessage(chat_id=new_chat.id, chat_name=new_chat.name, creator=creator)
        asyncio.run(new_chat_message.send_all())

    def get_many(self, user: models.User) -> dict[str, models.ChatMessages]:
        """Получение всех сообщений пользователя по чатам"""
        chat_creator = aliased(tables.User)

        messages = (
            self.session
            .query(
                tables.Chat.id.label("chat_id"),
                tables.Chat.name.label("chat_name"),
                tables.Message.id.label("message_id"),
                tables.Message.time.label("time"),
                tables.Message.text.label("text"),
                tables.User.login.label("login"),
                tables.Profile.avatar_file.label("avatar_file"),
                chat_creator.login.label("creator")
            )
            .distinct()
            .join(tables.Message, tables.Chat.id == tables.Message.chat_id, isouter=True)
            .join(tables.User, tables.Message.user_id == tables.User.id, isouter=True)
            .join(tables.Profile, tables.User.id == tables.Profile.user, isouter=True)
            .join(chat_creator, tables.Chat.creator_id == chat_creator.id)
            .where(
                and_(
                    tables.Chat.id == tables.ChatMember.chat_id,
                    tables.ChatMember.user_id == user.id
                )
            )
            .order_by(tables.Message.time)
            .all()
        )

        messages_data = [models.ChatData(**data) for data in messages]

        return self._convert_messages_to_chats(chats_data=messages_data)

    @staticmethod
    def _convert_messages_to_chats(chats_data: list[models.ChatData]) -> dict[str, models.ChatMessages]:
        chats = OrderedDict()

        for chat_data in chats_data:
            if chat_data.chat_id not in chats:
                chats[chat_data.chat_id] = models.ChatMessages(
                    chat_name=chat_data.chat_name,
                    creator=chat_data.creator,
                    messages=[]
                )

            if chat_data.message_id:
                chats[chat_data.chat_id].messages.append(models.MessageData.from_orm(chat_data))

        return chats

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

        chat = self._chat_members_service.get_chat_by_id(chat_id=chat_id)
        chat.name = new_name
        self.session.add(chat)
        self.session.commit()

        logger.info(f"Для чата {chat_id} установлено название: {new_name}")
        self._notify_about_change_chat_name(changed_chat=chat)

    def _is_user_chat_creator(self, chat_id: str, user: models.User) -> bool:
        """Является ли пользователь создателем чата"""
        chat = self._chat_members_service.get_chat_by_id(chat_id=chat_id)

        return chat.creator_id == user.id


    @staticmethod
    def _notify_about_change_chat_name(changed_chat: tables.Chat) -> None:
        """ws уведомление участников чата об изменении названия чата"""
        new_chat_message = ChangeChatNameMessage(chat_id=changed_chat.id, chat_name=changed_chat.name)
        asyncio.run(new_chat_message.send_all())
