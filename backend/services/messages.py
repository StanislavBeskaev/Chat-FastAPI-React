from collections import OrderedDict
from datetime import datetime

from pydantic import BaseModel, validator

from .. import tables
from . import BaseService
from .ws import get_formatted_time


class MessageData(BaseModel):
    message_id: str | None  # TODO надо синхронизировать эту модель и ws.TextMessageData
    time: str | datetime | None
    text: str | None
    login: str | None
    avatar_file: str | None

    class Config:
        orm_mode = True

    @validator("time")
    def convert_from_datetime(cls, value):
        if isinstance(value, datetime):
            return get_formatted_time(value)

        return value


class ChatData(MessageData):
    chat_id: str
    chat_name: str


class Chat(BaseModel):
    chat_name: str
    messages: list[MessageData]


class MessageService(BaseService):
    """Сервис для работы с сообщениями"""

    # TODO получение сообщений по указанному пользователю
    def get_many(self) -> dict[str, Chat]:
        """Получение всех сообщений по чатам"""
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
            .join(tables.Message, tables.Chat.id == tables.Message.chat_id, isouter=True)
            .join(tables.User, tables.Message.user_id == tables.User.id, isouter=True)
            .join(tables.Profile, tables.User.id == tables.Profile.user, isouter=True)
            .order_by(tables.Message.time)
            .all()
        )

        messages_data = [ChatData(**data) for data in messages]

        return self._convert_messages_to_chats(chats_data=messages_data)

    @staticmethod
    def _convert_messages_to_chats(chats_data: list[ChatData]) -> dict[str, Chat]:
        chats = OrderedDict()

        for chat_data in chats_data:
            if chat_data.chat_id not in chats:
                chats[chat_data.chat_id] = Chat(chat_name=chat_data.chat_name, messages=[])

            if chat_data.message_id:
                chats[chat_data.chat_id].messages.append(MessageData.from_orm(chat_data))

        return chats
