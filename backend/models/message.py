from pydantic import BaseModel

from .ws import WSMessageData


class MessageData(WSMessageData):
    message_id: str | None
    avatar_file: str | None

    class Config:
        orm_mode = True


class ChatChangeNameData(BaseModel):
    chat_id: str
    chat_name: str


class AddToChatData(ChatChangeNameData):
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

