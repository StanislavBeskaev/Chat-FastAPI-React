from datetime import datetime

from pydantic import BaseModel, validator, Field

from backend.core.time import get_formatted_time


class WSMessageData(BaseModel):
    """Данные WS сообщения"""
    login: str | None
    text: str | None
    time: str | datetime | None

    @validator("time")
    def convert_from_datetime(cls, value):
        if isinstance(value, datetime):
            return get_formatted_time(value)

        return value


class TextMessageData(WSMessageData):
    """Данные текстового сообщения"""
    message_id: str
    chat_id: str
    avatar_file: str | None  # TODO подумать как доставлять файл аватара на frontend


class InTextMessageData(BaseModel):
    """Данные входящего текстового сообщения"""
    chat_id: str = Field(alias="chatId")
    text: str | None


class InTypingMessageData(BaseModel):
    """Данные входящего сообщения о начале печатания"""
    chat_id: str = Field(alias="chatId")


class TypingMessageData(WSMessageData):
    """Данные сообщения о печатании"""
    chat_id: str
