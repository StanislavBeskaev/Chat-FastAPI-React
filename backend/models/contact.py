from pydantic import BaseModel


class ContactCreate(BaseModel):
    login: str


class ContactDelete(ContactCreate):
    pass


class Contact(ContactCreate):
    login: str
    name: str
    surname: str
    avatar_file: str
