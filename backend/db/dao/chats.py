from uuid import uuid4

from fastapi import HTTPException
from loguru import logger

from backend import tables, models
from backend.core.decorators import model_result
from backend.db.dao.base_dao import BaseDAO


class ChatsDAO(BaseDAO):
    """Класс для работы с чатами в БД"""

    @model_result(models.Chat)
    def get_all_chats(self) -> list[models.Chat]:
        """Получение всех записей из таблицы чатов"""
        db_chats = (
            self.session
            .query(tables.Chat)
            .all()
        )

        return db_chats

    @model_result(models.Chat)
    def get_chat_by_id(self, chat_id: str) -> models.Chat:
        """Получение чата по id"""
        db_chat = self._get_chat_by_id(chat_id=chat_id)

        if not db_chat:
            error = f"Чата с id {chat_id} не существует"
            logger.warning(error)
            raise HTTPException(status_code=404, detail=error)

        return db_chat

    def _get_chat_by_id(self, chat_id: str) -> tables.Chat:
        db_chat = (
            self.session
            .query(tables.Chat)
            .where(tables.Chat.id == chat_id)
            .first()
        )

        return db_chat

    @model_result(models.Chat)
    def create_chat(self, chat_name: str, creator_id: int) -> models.Chat:
        """Создание нового чата"""
        new_chat = tables.Chat(
            id=str(uuid4()),
            name=chat_name,
            creator_id=creator_id
        )
        self.session.add(new_chat)
        self.session.commit()

        return new_chat

    @model_result(models.Chat)
    def change_chat_name(self, chat_id: str, new_name: str) -> models.Chat:
        """Изменение названия чата"""
        chat = self._get_chat_by_id(chat_id=chat_id)
        chat.name = new_name
        self.session.add(chat)
        self.session.commit()

        return chat
