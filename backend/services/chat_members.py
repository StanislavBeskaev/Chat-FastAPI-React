import asyncio

from fastapi import Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from loguru import logger

from backend import models, tables
from backend.database import get_session
from backend.services import BaseService
from backend.services.get_chat_members import get_chat_members
from backend.services.user import UserService
from backend.services.ws import AddToChatMessage, DeleteFromChatMessage
from backend.services.ws_connection_manager import WSConnectionManager


class ChatMembersService(BaseService):
    """Сервис для работы с участниками чатов"""

    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session=session)
        self._user_service = UserService(session=session)

    def add_login_to_chat(self, login: str, chat_id: str) -> None:
        """Добавление пользователя по логину к чату. Если пользователь уже есть в чате, то ничего не происходит"""
        user = self._user_service.find_user_by_login(login=login)
        self.add_user_to_chat(user=user, chat_id=chat_id)

        chat = self.get_chat_by_id(chat_id=chat_id)
        add_to_chat_message = AddToChatMessage(chat_id=chat_id, chat_name=chat.name, login=login)
        asyncio.run(add_to_chat_message.send())

    def delete_login_from_chat(self, login: str, chat_id: str) -> None:
        """Удаление пользователя по логину из чата"""
        user = self._user_service.find_user_by_login(login=login)
        chat_member = self.find_chat_member(user_id=user.id, chat_id=chat_id)

        if not chat_member:
            raise HTTPException(status_code=404, detail=f"Пользователя {login} нет в чате")

        self.session.delete(chat_member)
        self.session.commit()

        chat = self.get_chat_by_id(chat_id=chat_id)
        delete_from_chat_message = DeleteFromChatMessage(chat_id=chat_id, chat_name=chat.name, login=login)
        asyncio.run(delete_from_chat_message.send())

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

    def find_chat_member(self, user_id: int, chat_id: str) -> tables.ChatMember | None:
        candidate = (
            self.session
            .query(tables.ChatMember)
            .where(
                and_(
                    tables.ChatMember.chat_id == chat_id,
                    tables.ChatMember.user_id == user_id
                )
            )
            .first()
        )

        return candidate

    def is_user_in_chat(self, user: models.User, chat_id: str) -> bool:
        """Есть ли пользователь в чате"""

        return self.find_chat_member(user_id=user.id, chat_id=chat_id) is not None

    def get_chat_by_id(self, chat_id: str) -> tables.Chat:
        """Получение чата по id"""
        chat = (
            self.session
            .query(tables.Chat)
            .where(tables.Chat.id == chat_id)
            .first()
        )

        if not chat:
            logger.warning(f"Чата с id {chat_id} не существует")
            raise HTTPException(status_code=404, detail="Чата с таким id не существует")

        return chat

    @staticmethod
    def get_chat_members_with_online_status(chat_id: str) -> list[models.ChatMemberWithOnlineStatus]:
        """Получение информации об участниках чата и их онлайн статусе"""
        chat_members = get_chat_members(chat_id=chat_id)
        active_logins = WSConnectionManager().get_active_logins()

        chat_members_with_online_status = [
            models.ChatMemberWithOnlineStatus(
                login=member.login,
                is_online=member.login in active_logins
            )
            for member in chat_members
        ]

        return chat_members_with_online_status
