from pydantic import BaseModel


class ChatMemberWithOnlineStatus(BaseModel):
    login: str
    is_online: bool
