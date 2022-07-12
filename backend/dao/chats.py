from uuid import uuid4

from fastapi import HTTPException
from loguru import logger

from backend import tables, models
from backend.dao import BaseDAO


class ChatsDAO(BaseDAO):
    """Класс для работы с чатами в БД"""

    def get_chat_by_id(self, chat_id: str) -> models.Chat:
        """Получение чата по id"""
        db_chat = (
            self.session
            .query(tables.Chat)
            .where(tables.Chat.id == chat_id)
            .first()
        )

        if not db_chat:
            logger.warning(f"Чата с id {chat_id} не существует")
            raise HTTPException(status_code=404, detail="Чата с таким id не существует")

        return models.Chat.from_orm(db_chat)

    def create_chat(self, chat_name: str, creator_id: int) -> models.Chat:
        """Создание нового чата"""
        new_chat = tables.Chat(
            id=str(uuid4()),
            name=chat_name,
            creator_id=creator_id
        )
        self.session.add(new_chat)
        self.session.commit()

        return models.Chat.from_orm(new_chat)
