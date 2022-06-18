from pydantic import BaseModel

from .ws import WSMessageData


class MessageData(WSMessageData):
    message_id: str | None
    avatar_file: str | None

    class Config:
        orm_mode = True


class NewChatData(BaseModel):
    chat_id: str
    chat_name: str


class ChatData(MessageData, NewChatData):
    pass


class ChatMessages(BaseModel):
    chat_name: str
    messages: list[MessageData]


class ChatCreate(BaseModel):
    chat_name: str
    members: list[str]
