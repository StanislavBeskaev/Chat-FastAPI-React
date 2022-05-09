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

    def register_new_user(self, user_data: models.UserCreate) -> models.Tokens:
        """Регистрация нового пользователя"""
        logger.debug(f"Попытка регистрации нового пользователя по данным: {user_data}")
        if self._find_user_by_login(login=user_data.login):
            logger.warning(f"Пользователь с логином '{user_data.login}' уже существует")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким логином уже существует"
            )

        new_user = self._create_new_user(user_data=user_data)
        tokens = TokenService.generate_tokens(user=new_user)

        return tokens

    def _find_user_by_login(self, login: str) -> tables.User | None:
        """Поиск пользователя по login"""
        user = (
            self.session
            .query(tables.User)
            .filter(tables.User.login == login)
            .first()
        )

        return user

    def _create_new_user(self, user_data: models.UserCreate) -> models.User:
        """Создание нового пользователя"""
        new_user = tables.User(
            login=user_data.login,
            password=self.hash_password(user_data.password)
        )
        self.session.add(new_user)
        self.session.commit()

        new_user = models.User.from_orm(new_user)
        logger.info(f"Создан новый пользователь: {new_user}")

        return new_user
