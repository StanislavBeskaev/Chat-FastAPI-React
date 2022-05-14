from pydantic import BaseModel, Field


# TODO валидация
class UserBase(BaseModel):
    login: str


class UserUpdate(BaseModel):
    name: str = Field(default='')
    surname: str = Field(default='')


# TODO валидация
class UserCreate(UserBase, UserUpdate):
    password: str


class UserLogin(UserBase):
    password: str


class User(UserBase, UserUpdate):
    id: int

    class Config:
        orm_mode = True
