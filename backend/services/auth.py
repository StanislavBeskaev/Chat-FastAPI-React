from fastapi import HTTPException, status
from loguru import logger
from passlib.hash import bcrypt

from .. import models, tables
from . import BaseService
from .token import TokenService


class AuthService(BaseService):
    """Сервис авторизации и регистрации"""

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    # TODO возвращаемое значение c токенами
    def registration(self, user_data: models.UserCreate) -> models.Tokens:
        """Регистрация нового пользователя"""
        logger.info(f"Попытка регистрации нового пользователя по данным: {user_data}")
        if self._find_user_by_email(email=user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email уже существует"
            )

        new_user = self._create_new_user(user_data=user_data)
        # TODO generateTokens, saveToken, return {...tokens, user: userDto}
        tokens = TokenService.generate_tokens(user=new_user)

        return tokens

    # TODO подумать, может вынести в UserService?
    def _find_user_by_email(self, email: str) -> tables.User | None:
        """Поиск пользователя по email"""
        user = (
            self.session
            .query(tables.User)
            .filter(tables.User.email == email)
            .first()
        )

        return user

    # TODO подумать, может вынести в UserService?
    def _create_new_user(self, user_data: models.UserCreate) -> models.User:
        """Создание нового пользователя"""
        new_user = tables.User(
            email=user_data.email,
            password=self.hash_password(user_data.password)
        )
        self.session.add(new_user)
        self.session.commit()

        new_user = models.User.from_orm(new_user)
        logger.info(f"Создан новый пользователь: {new_user}")

        return new_user
