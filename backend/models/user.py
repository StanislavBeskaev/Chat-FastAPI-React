from pydantic import BaseModel


# TODO валидация
class UserBase(BaseModel):
    email: str


# TODO валидация
class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True
