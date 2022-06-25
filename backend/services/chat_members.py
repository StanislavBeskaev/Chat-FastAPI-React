from fastapi import Depends
from sqlalchemy import and_
from sqlalchemy.orm import Session
from loguru import logger

from backend import models, tables
from backend.database import get_session
from backend.services import BaseService
from backend.services.user import UserService
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
        # TODO ws сообщение о добавлении пользователя к чату

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
        """Получение пользователей - участников чата"""
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

    def get_chat_members_with_online_status(self, chat_id: str) -> list[models.ChatMemberWithOnlineStatus]:
        """Получение информации об участниках чата и их онлайн статусе"""
        chat_members = self.get_chat_members(chat_id=chat_id)
        active_logins = WSConnectionManager().get_active_logins()

        chat_members_with_online_status = [
            models.ChatMemberWithOnlineStatus(
                login=member.login,
                is_online=member.login in active_logins
            )
            for member in chat_members
        ]

        return chat_members_with_online_status
