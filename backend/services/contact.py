from fastapi import HTTPException, status, Depends
from loguru import logger
from sqlalchemy.orm import Session

from .. import models
from .. import tables
from ..database import get_session
from . import BaseService
from .user import UserService


class ContactService(BaseService):
    """Сервис для управления контактами"""

    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session=session)
        self._user_service = UserService(session=session)

    def get_many(self, user: models.User) -> list[models.Contact]:
        """Получение контактов пользователя"""
        logger.debug(f"Запрос на получение контактов пользователя: {user.login}")

        contacts = (
            self.session
            .query(
                tables.User.login,
                tables.Contact.name,
                tables.Contact.surname,
                tables.Profile.avatar_file
            )
            .where(tables.Contact.owner_user_id == user.id)
            .where(tables.User.id == tables.Profile.user)
            .where(tables.User.id == tables.Contact.contact_user_id)
        )

        contacts = [
            models.Contact(
                login=contact_info[0],
                name=contact_info[1],
                surname=contact_info[2],
                avatar_file=contact_info[3]
            )
            for contact_info in contacts
        ]

        logger.debug(f"Контакты пользователя {user.login}: {contacts}")
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

        contact_user_info = self._user_service.get_user_info(login=contact_login)

        new_contact = tables.Contact(
            owner_user_id=user.id,
            contact_user_id=contact_user_info.id,
            name=contact_user_info.name,
            surname=contact_user_info.surname
        )

        self.session.add(new_contact)
        self.session.commit()

        logger.info(f"Для пользователя '{user.login}' добавлен новый контакт: '{contact_login}'")

        return models.Contact(
            login=contact_login,
            name=contact_user_info.name,
            surname=contact_user_info.surname,
            avatar_file=contact_user_info.avatar_file
        )

    def delete(self, user: models.User, contact_login: str) -> None:
        """Удаление контакта по логину"""
        logger.debug(f"Пользователь {user.login} попытка удаления контакта {contact_login}")
        contact = self._find_contact(user=user, contact_login=contact_login)

        if not contact:
            logger.warning(f"Пользователь {user.login} попытка удаления "
                           f"не существующего контакта {contact_login}")
            raise self._get_not_found_contact_exception(contact_login=contact_login)

        self.session.delete(contact)
        self.session.commit()

        logger.info(f"Пользователь {user.login} удалён контакт {contact_login}")

    def get_by_login(self, user: models.User, contact_login: str):
        """Получение контакта по логину"""
        logger.debug(f"Пользователь {user.login} запрос данных контакта {contact_login}")
        contact = self._find_contact(user=user, contact_login=contact_login)

        if not contact:
            logger.warning(f"Пользователь {user.login} запрос данных "
                           f"не существующего контакта {contact_login}")
            raise self._get_not_found_contact_exception(contact_login=contact_login)

        contact_user_info = self._user_service.get_user_info(login=contact_login)

        return models.Contact(
            login=contact_login,
            name=contact.name,
            surname=contact.surname,
            avatar_file=contact_user_info.avatar_file
        )

    def change(self, user: models.User, contact_data: models.ContactChange) -> None:
        """Изменение данных контакта(имя, фамилия)"""
        logger.debug(f"Пользователь {user.login} попытка изменения контакта {contact_data}")
        contact = self._find_contact(user=user, contact_login=contact_data.login)

        if not contact:
            logger.warning(f"Пользователь {user.login} попытка изменения "
                           f"не существующего контакта {contact_data.login}")
            raise self._get_not_found_contact_exception(contact_login=contact_data.login)

        contact.name = contact_data.name
        contact.surname = contact_data.surname
        self.session.add(contact)
        self.session.commit()

    def _find_contact(self, user: models.User, contact_login: str) -> tables.Contact | None:
        contact_user = self._user_service.find_user_by_login(login=contact_login)

        if not contact_user:
            logger.warning(f"Пользователь {user.login} операция"
                           f" с не существующим пользователем {contact_login}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с логином '{contact_login}' не найден"
            )

        contact = (
            self.session
            .query(tables.Contact)
            .where(tables.Contact.owner_user_id == user.id)
            .where(tables.Contact.contact_user_id == contact_user.id)
            .first()
        )

        return contact

    @staticmethod
    def _get_not_found_contact_exception(contact_login: str) -> HTTPException:
        return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Контакт с логином '{contact_login}' не найден"
            )
