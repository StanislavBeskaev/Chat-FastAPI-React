from pydantic import BaseModel


class Chat(BaseModel):
    id: str
    name: str
    is_public: bool
    creator_id: int

    class Config:
        orm_mode = True
