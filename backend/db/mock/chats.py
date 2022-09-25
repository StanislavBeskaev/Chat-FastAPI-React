from uuid import uuid4

from fastapi import HTTPException
from loguru import logger

from backend import tables, models
from backend.core.decorators import model_result


class MockChatsDAO:
    """Mock класс для работы с чатами в БД"""

    chats: list[tables.Chat]

    @model_result(models.Chat)
    def get_all_chats(self) -> list[models.Chat]:
        """Получение всех записей из таблицы чатов"""
        return self.chats

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
        db_chat = next(
            (chat for chat in self.chats if chat.id == chat_id),
            None
        )

        return db_chat

    @model_result(models.Chat)
    def create_chat(self, chat_name: str, creator_id: int) -> models.Chat:
        """Создание нового чата"""
        new_chat = tables.Chat(
            id=str(uuid4()),
            name=chat_name,
            creator_id=creator_id,
            is_public=False
        )
        self.chats.append(new_chat)

        return new_chat

    @model_result(models.Chat)
    def change_chat_name(self, chat_id: str, new_name: str) -> models.Chat:
        """Изменение названия чата"""
        chat = self._get_chat_by_id(chat_id=chat_id)
        chat.name = new_name

        return chat
