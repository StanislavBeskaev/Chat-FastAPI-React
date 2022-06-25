from loguru import logger
from sqlalchemy import and_

from backend import models, tables
from backend.database import get_session


def get_chat_members(chat_id: str) -> list[models.User]:
    """Получение пользователей - участников чата"""
    session = next(get_session())
    users_in_chat = (
        session
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
