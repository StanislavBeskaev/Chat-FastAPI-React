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

    class Config:
        orm_mode = True


class ContactFull(BaseModel):
    id: int
    owner_user_id: int
    contact_user_id: int
    name: str
    surname: str

    class Config:
        orm_mode = True
