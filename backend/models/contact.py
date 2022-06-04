from pydantic import BaseModel


class ContactCreate(BaseModel):
    login: str


class ContactDelete(ContactCreate):
    pass


class ContactChange(ContactCreate):
    name: str
    surname: str


class Contact(ContactChange):
    avatar_file: str
