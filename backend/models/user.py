from pydantic import BaseModel


# TODO валидация
class UserBase(BaseModel):
    login: str


# TODO валидация
class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True
