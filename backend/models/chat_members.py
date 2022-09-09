from pydantic import BaseModel


class ChatMember(BaseModel):
    login: str


class ChatMemberWithOnlineStatus(ChatMember):
    is_online: bool


class ChatMemberFull(BaseModel):
    id: int
    chat_id: str
    user_id: int

    class Config:
        orm_mode = True
