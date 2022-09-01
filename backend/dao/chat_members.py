from loguru import logger
from sqlalchemy import and_

from backend import tables, models
from backend.dao import BaseDAO


class ChatMembersDAO(BaseDAO):
    """Класс для работы с участниками чатов в БД"""

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
        user_logins = [user.login for user in users]
        logger.debug(f"Участники чата {chat_id}: {user_logins}")
        return users

    def find_chat_member(self, user_id: int, chat_id: str) -> tables.ChatMember | None:
        """Поиск участника чата"""
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

    def add_chat_member(self, user_id: int, chat_id: str) -> None:
        """Добавление участника к чату"""
        new_chat_member = tables.ChatMember(
            chat_id=chat_id,
            user_id=user_id
        )

        self.session.add(new_chat_member)
        self.session.commit()

    def delete_chat_member(self, chat_member: tables.ChatMember) -> None:
        """Удаление участника из чата"""
        self.session.delete(chat_member)
        self.session.commit()
