from datetime import datetime

from pydantic import BaseModel, validator

from backend import tables
from backend.core.time import get_formatted_time
from backend.models.ws import WSMessageData


class ChangeMessageText(BaseModel):
    text: str


class DeleteMessageData(BaseModel):
    chat_id: str
    message_id: str


class ChangeMessageTextData(ChangeMessageText, DeleteMessageData):
    change_time: str | None


class Message(BaseModel):
    id: str
    chat_id: str
    text: str
    user_id: int
    time: datetime
    type: str

    class Config:
        orm_mode = True


class MessageFull(Message):
    change_time: datetime | None


class MessageReadStatus(BaseModel):
    id: int
    message_id: str
    user_id: str
    is_read: bool

    class Config:
        orm_mode = True


class MessageData(WSMessageData):
    message_id: str | None
    type: str | None = tables.MessageType.TEXT
    is_read: bool | None = True
    change_time: str | datetime | None

    @classmethod
    @validator("change_time")
    def convert_from_datetime(cls, value):
        if isinstance(value, datetime):
            return get_formatted_time(value)

        return value

    @classmethod
    @validator("is_read")
    def is_read_default_true(cls, value):
        if value is None:
            return True

        return value

    class Config:
        orm_mode = True


class ChatChangeNameData(BaseModel):
    chat_id: str
    chat_name: str


class ChatNameData(ChatChangeNameData):
    pass


class NewChatData(ChatChangeNameData):
    creator: str


class ChatData(MessageData, NewChatData):
    pass


class ChatMessages(BaseModel):
    chat_name: str
    creator: str
    messages: list[MessageData]


class ChatUpdateName(BaseModel):
    chat_name: str


class ChatCreate(ChatUpdateName):
    members: list[str]

