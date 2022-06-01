from fastapi import HTTPException, status, Depends
from loguru import logger
from sqlalchemy.orm import Session

from .. import models
from .. import tables
from ..database import get_session
from . import BaseService
from .auth import AuthService


class ContactService(BaseService):
    """Сервис для управления контактами"""

    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session=session)
        self._auth_service = AuthService(session=session)

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

    def create(self, user: models.User, contact_login: str) -> None:
        """Создание нового контакта"""
        if user.login == contact_login:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя добавить себя в контакты"
            )

        if self._find_contact(user=user, contact_login=contact_login):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Такой контакт уже существует"
            )

        # TODO убрать повторение тут в и _find_contact
        contact_user = self._auth_service.find_user_by_login(login=contact_login)

        new_contact = tables.Contact(
            owner_user_id=user.id,
            contact_user_id=contact_user.id,
            name=contact_user.name,
            surname=contact_user.surname
        )

        self.session.add(new_contact)
        self.session.commit()

        logger.info(f"Для пользователя '{user.login}' добавлен новый контакт: '{contact_login}'")

    def _find_contact(self, user: models.User, contact_login: str) -> tables.Contact | None:
        contact_user = self._auth_service.find_user_by_login(login=contact_login)

        if not contact_user:
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
