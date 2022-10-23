from pydantic import BaseModel


class Chat(BaseModel):
    id: str
    name: str
    is_public: bool
    creator_id: int

    class Config:
        orm_mode = True


class LeaveChat(BaseModel):
    chat_id: str
    chat_name: str


class DeleteChat(BaseModel):
    login: str
    chat_id: str
    chat_name: str
