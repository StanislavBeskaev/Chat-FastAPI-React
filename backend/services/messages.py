from collections import OrderedDict
from uuid import uuid4

from fastapi import Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from loguru import logger

from backend import models, tables
from backend.database import get_session
from backend.services import BaseService
from backend.services.user import UserService


class MessageService(BaseService):
    """Сервис для работы с сообщениями и чатами"""

    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session=session)
        self._user_service = UserService(session=session)

    def create_chat(self, chat_data: models.ChatCreate) -> None:
        """Создание чата"""
        logger.debug(f"Попытка создания нового чата, {chat_data=}")
        chat_users = self._validate_new_chat_data(chat_data=chat_data)

        new_chat = tables.Chat(
            id=str(uuid4()),
            name=chat_data.chat_name
        )
        self.session.add(new_chat)
        self.session.commit()
        for user in chat_users:
            self.add_user_to_chat(user=user, chat_id=new_chat.id)

        logger.info(f"Создан новый чат {new_chat.name} с id {new_chat.id}")

        # TODO WS сообщение о новом чате всем участникам

    def _validate_new_chat_data(self, chat_data: models.ChatCreate) -> list[models.User]:
        """Проверка данных для создания нового чата"""
        if not chat_data.chat_name:
            logger.error(f"Не указано имя чата")
            raise HTTPException(status_code=400, detail="Не указано имя чата")

        if not chat_data.members:
            logger.error(f"Не указаны участники чата")
            raise HTTPException(status_code=400, detail="Не указаны участники чата")

        chat_users = [self._user_service.find_user_by_login(login) for login in chat_data.members]
        if not all(chat_users):
            logger.error(f"В списке участников есть не существующие пользователи")
            raise HTTPException(status_code=400, detail="В списке участников есть не существующие пользователи")

        chat_users = [models.User.from_orm(user) for user in chat_users]
        logger.debug(f"{chat_users=}")
        return chat_users

    def add_user_to_chat(self, user: models.User, chat_id: str) -> None:
        """Добавление пользователя к чату. Если пользователь уже есть в чате, то ничего не происходит"""
        logger.debug(f"Попытка добавить к чату {chat_id} пользователя {user}")
        if self.is_user_in_chat(user=user, chat_id=chat_id):
            logger.warning(f"В чате {chat_id} уже есть пользователь {user}")
            return

        new_chat_member = tables.ChatMember(
            chat_id=chat_id,
            user_id=user.id
        )

        self.session.add(new_chat_member)
        self.session.commit()

        logger.info(f"К чату {chat_id} добавлен пользователь {user}")

    def is_user_in_chat(self, user: models.User, chat_id: str) -> bool:
        """Есть ли пользователь в чате"""
        candidate = (
            self.session
            .query(tables.ChatMember)
            .where(
                and_(
                    tables.ChatMember.chat_id == chat_id,
                    tables.ChatMember.user_id == user.id
                )
            )
            .first()
        )

        return candidate is not None

    def get_chat_members(self, chat_id: str) -> list[models.User]:
        users_in_chat = (
            self.session
            .query(tables.User)
            .where(
                and_(
                    tables.User.id == tables.ChatMember.user_id,
                    tables.ChatMember.chat_id == chat_id
                )
            )
            .all()
        )

        users = [models.User.from_orm(user) for user in users_in_chat]
        logger.debug(f"Участники чата {chat_id}: {users}")
        return users

    def get_many(self, user: models.User) -> dict[str, models.ChatMessages]:
        """Получение всех сообщений пользователя по чатам"""
        messages = (
            self.session
            .query(
                tables.Chat.id.label("chat_id"),
                tables.Chat.name.label("chat_name"),
                tables.Message.id.label("message_id"),
                tables.Message.time.label("time"),
                tables.Message.text.label("text"),
                tables.User.login.label("login"),
                tables.Profile.avatar_file.label("avatar_file")
            )
            .distinct()
            .join(tables.Message, tables.Chat.id == tables.Message.chat_id, isouter=True)
            .join(tables.User, tables.Message.user_id == tables.User.id, isouter=True)
            .join(tables.Profile, tables.User.id == tables.Profile.user, isouter=True)
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
                chats[chat_data.chat_id] = models.ChatMessages(chat_name=chat_data.chat_name, messages=[])

            if chat_data.message_id:
                chats[chat_data.chat_id].messages.append(models.MessageData.from_orm(chat_data))

        return chats
