from pydantic import BaseModel, Field


class UserBase(BaseModel):
    login: str


class UserUpdate(BaseModel):
    name: str = Field(default='')
    surname: str = Field(default='')


class UserCreate(UserBase, UserUpdate):
    password: str


class UserLogin(UserBase):
    password: str


class User(UserBase, UserUpdate):
    id: int

    class Config:
        orm_mode = True


class Profile(BaseModel):
    id: int
    user: int
    avatar_file: str

    class Config:
        orm_mode = True
