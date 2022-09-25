from fastapi import HTTPException, status
from loguru import logger

from backend import models, tables
from backend.services import BaseService


class ContactService(BaseService):
    """Сервис для управления контактами"""
    def get_many(self, user: models.User) -> list[models.Contact]:
        """Получение контактов пользователя"""
        logger.debug(f"Запрос на получение контактов пользователя: {user.login}")
        contacts = self._db_facade.get_user_contacts(user_id=user.id)
        logger.debug(f"Контакты пользователя {user}: {contacts}")

        return contacts

    def create(self, user: models.User, contact_login: str) -> models.Contact:
        """Создание нового контакта"""
        logger.debug(f"Пользователь {user.login} попытка добавить в контакты {contact_login}")

        if user.login == contact_login:
            logger.warning(f"Пользователь {user.login} попытка добавить себя в контакты")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя добавить себя в контакты"
            )

        if self._find_contact(user=user, contact_login=contact_login):
            logger.warning(f"Пользователь {user.login} попытка добавить уже существующий контакт {contact_login}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Такой контакт уже существует"
            )

        # Тут будет 404 если пользователь не найден
        contact_user_info = self._db_facade.get_user_info(login=contact_login)

        self._db_facade.create_contact(
            owner_user_id=user.id,
            contact_user_id=contact_user_info.id,
            name=contact_user_info.name,
            surname=contact_user_info.surname
        )
        logger.info(f"Для пользователя '{user.login}' добавлен новый контакт: '{contact_login}'")

        return models.Contact(
            login=contact_login,
            name=contact_user_info.name,
            surname=contact_user_info.surname
        )

    def delete(self, user: models.User, contact_login: str) -> None:
        """Удаление контакта по логину"""
        logger.debug(f"Пользователь {user.login} попытка удаления контакта {contact_login}")
        contact = self._find_contact(user=user, contact_login=contact_login)

        if not contact:
            logger.warning(f"Пользователь {user.login} попытка удаления "
                           f"не существующего контакта {contact_login}")
            raise self._get_not_found_contact_exception(contact_login=contact_login)

        self._db_facade.delete_contact(contact=contact)

        logger.info(f"Пользователь {user.login} удалён контакт {contact_login}")

    def get_by_login(self, user: models.User, contact_login: str):
        """Получение контакта по логину"""
        logger.debug(f"Пользователь {user.login} запрос данных контакта {contact_login}")
        contact = self._find_contact(user=user, contact_login=contact_login)

        if not contact:
            logger.warning(f"Пользователь {user.login} запрос данных "
                           f"не существующего контакта {contact_login}")
            raise self._get_not_found_contact_exception(contact_login=contact_login)

        return models.Contact(
            login=contact_login,
            name=contact.name,
            surname=contact.surname
        )

    def change(self, user: models.User, contact_data: models.ContactChange) -> None:
        """Изменение данных контакта(имя, фамилия)"""
        logger.debug(f"Пользователь {user.login} попытка изменения контакта {contact_data}")
        contact = self._find_contact(user=user, contact_login=contact_data.login)

        if not contact:
            logger.warning(f"Пользователь {user.login} попытка изменения "
                           f"не существующего контакта {contact_data.login}")
            raise self._get_not_found_contact_exception(contact_login=contact_data.login)

        self._db_facade.change_contact(
            contact=contact,
            new_name=contact_data.name,
            new_surname=contact_data.surname
        )

    def _find_contact(self, user: models.User, contact_login: str) -> tables.Contact | None:
        contact_user = self._db_facade.find_user_by_login(login=contact_login)

        if not contact_user:
            logger.warning(f"Пользователь {user.login} операция"
                           f" с не существующим пользователем {contact_login}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с логином '{contact_login}' не найден"
            )

        return self._db_facade.find_contact(owner_user_id=user.id, contact_user_id=contact_user.id)

    @staticmethod
    def _get_not_found_contact_exception(contact_login: str) -> HTTPException:
        return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Контакт с логином '{contact_login}' не найден"
            )
