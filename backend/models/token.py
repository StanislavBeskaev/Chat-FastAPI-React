from pydantic import BaseModel

from .user import User


# TODO подумать, может разбить поменьше
class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    user: User
