from pydantic import BaseModel

from backend import tables
from .ws import WSMessageData


class MessageData(WSMessageData):
    message_id: str | None
    type: str | None = tables.MessageType.TEXT

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

