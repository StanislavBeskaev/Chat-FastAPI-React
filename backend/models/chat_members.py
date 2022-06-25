from pydantic import BaseModel


class ChatMember(BaseModel):
    login: str


class ChatMemberWithOnlineStatus(ChatMember):
    is_online: bool
