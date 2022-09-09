from pydantic import BaseModel

from backend.models.user import User


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    user: User


class RefreshToken(BaseModel):
    id: int
    user: int
    refresh_token: str
    user_agent: str

    class Config:
        orm_mode = True
