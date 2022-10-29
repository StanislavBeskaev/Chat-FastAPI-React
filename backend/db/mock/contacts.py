from backend import tables, models
from backend.core.decorators import model_result
from backend.db.mock.users import MockUsersDAO


class MockContactsDAO:
    """Mock класс для работы с контактами в БД"""

    contacts: list[tables.Contact]

    @model_result(models.ContactFull)
    def get_all_contacts(self) -> list[models.ContactFull]:
        """Получение всех записей таблицы контактов из базы"""
        return self.contacts

    def get_user_contacts(self, user_id: int, users_dao: MockUsersDAO) -> list[models.Contact]:
        """Получение контактов пользователя"""
        contacts = [
            {
                "login": users_dao.find_user_by_id(contact.contact_user_id).login,
                "name": contact.name,
                "surname": contact.surname,
            }
            for contact in self.contacts
            if contact.owner_user_id == user_id
        ]
        contacts = [models.Contact(**contact_info) for contact_info in contacts]

        return contacts

    def find_contact(self, owner_user_id: int, contact_user_id: int) -> tables.Contact | None:
        """Нахождение контакта пользователя"""
        db_contact = next(
            (
                contact
                for contact in self.contacts
                if contact.owner_user_id == owner_user_id and contact.contact_user_id == contact_user_id
            ),
            None,
        )

        return db_contact

    def create_contact(self, owner_user_id: int, contact_user_id: int, name: str, surname: str) -> tables.Contact:
        """Создание контакта"""
        new_contact = tables.Contact(
            id=max([contact.id for contact in self.contacts]) + 1,
            owner_user_id=owner_user_id,
            contact_user_id=contact_user_id,
            name=name,
            surname=surname,
        )
        self.contacts.append(new_contact)

        return new_contact

    def delete_contact(self, contact: tables.Contact) -> None:
        """Удаление контакта"""
        self.contacts.remove(contact)

    @staticmethod
    def change_contact(contact: tables.Contact, new_name: str, new_surname: str) -> None:
        """Изменение данных контакта"""
        contact.name = new_name
        contact.surname = new_surname
