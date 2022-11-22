from backend import models, tables
from backend.core.decorators import model_result
from backend.db.dao.base_dao import BaseDAO


class ContactsDAO(BaseDAO):
    """Класс для работы с контактами в БД"""

    @model_result(models.ContactFull)
    def get_all_contacts(self) -> list[models.ContactFull]:
        """Получение всех записей таблицы контактов из базы"""
        db_contacts = self.session.query(tables.Contact).all()

        return db_contacts

    def get_user_contacts(self, user_id: int) -> list[models.Contact]:
        """Получение контактов пользователя"""
        contacts = (
            self.session.query(
                tables.User.login.label("login"),
                tables.Contact.name.label("name"),
                tables.Contact.surname.label("surname"),
            )
            .where(tables.Contact.owner_user_id == user_id)
            .where(tables.User.id == tables.Profile.user)
            .where(tables.User.id == tables.Contact.contact_user_id)
        )

        contacts = [models.Contact(**contact_info) for contact_info in contacts]

        return contacts

    def find_contact(self, owner_user_id: int, contact_user_id: int) -> tables.Contact | None:
        """Нахождение контакта пользователя"""
        contact = (
            self.session.query(tables.Contact)
            .where(tables.Contact.owner_user_id == owner_user_id)
            .where(tables.Contact.contact_user_id == contact_user_id)
            .first()
        )

        return contact

    def create_contact(self, owner_user_id: int, contact_user_id: int, name: str, surname: str) -> tables.Contact:
        """Создание контакта"""
        new_contact = tables.Contact(
            owner_user_id=owner_user_id, contact_user_id=contact_user_id, name=name, surname=surname
        )

        self.session.add(new_contact)
        self.session.commit()

        return new_contact

    def delete_contact(self, contact: tables.Contact) -> None:
        """Удаление контакта"""
        self.session.delete(contact)
        self.session.commit()

    def change_contact(self, contact: tables.Contact, new_name: str, new_surname: str) -> None:
        """Изменение данных контакта"""
        contact.name = new_name
        contact.surname = new_surname
        self.session.add(contact)
        self.session.commit()
