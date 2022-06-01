from pydantic import BaseModel


class ContactCreate(BaseModel):
    login: str


class Contact(ContactCreate):
    login: str
    name: str
    surname: str
    avatar_file: str
