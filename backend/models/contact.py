from pydantic import BaseModel


class ContactCreate(BaseModel):
    login: str


class ContactDelete(ContactCreate):
    pass


class ContactChange(ContactCreate):
    name: str | None
    surname: str | None


class Contact(ContactChange):
    pass
