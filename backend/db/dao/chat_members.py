from loguru import logger
from sqlalchemy import and_

from backend import tables, models
from backend.core.decorators import model_result
from backend.db.dao.base_dao import BaseDAO


class ChatMembersDAO(BaseDAO):
    """Класс для работы с участниками чатов в БД"""

    @model_result(models.ChatMemberFull)
    def get_all_chat_members(self) -> list[models.ChatMemberFull]:
        """Получение всех записей таблицы участников чатов"""
        db_chat_members = (
            self.session
            .query(tables.ChatMember)
            .all()
        )

        return db_chat_members

    @model_result(models.User)
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

        user_logins = [user.login for user in users_in_chat]
        logger.debug(f"Участники чата {chat_id}: {user_logins}")
        return users_in_chat

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

    def delete_all_members_from_chat(self, chat_id: str) -> None:
        """Удаление всех участников чата"""
        chat_members_query = (
            self.session
            .query(tables.ChatMember)
            .where(tables.ChatMember.chat_id == chat_id)
        )
        chat_members_query.delete()
        logger.info(f"Удалены все участники чата {chat_id}")
