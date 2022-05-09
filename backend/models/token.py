from pydantic import BaseModel

from .user import User


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    user: User
