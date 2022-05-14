from fastapi import HTTPException, status
from loguru import logger
from passlib.hash import bcrypt
from pydantic import ValidationError

from .. import models, tables
from . import BaseService
from .token import TokenService


class AuthService(BaseService):
    """Сервис авторизации и регистрации"""

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)

    def register_new_user(self, user_data: models.UserCreate) -> models.Tokens:
        """Регистрация нового пользователя"""
        logger.debug(f"Попытка регистрации нового пользователя по данным: {user_data}")
        if self.find_user_by_login(login=user_data.login):
            logger.warning(f"Пользователь с логином '{user_data.login}' уже существует")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким логином уже существует"
            )

        new_user = self._create_new_user(user_data=user_data)
        tokens = TokenService.generate_tokens(user=new_user)

        return tokens

    def login_user(self, login: str, password: str) -> models.Tokens:
        """Авторизация пользователя"""
        logger.debug(f"Попытка авторизации с данными: {login=} {password=}")
        user = self.find_user_by_login(login)
        if not user:
            message = "Пользователь с таким логином не найден"
            logger.warning(message)
            raise HTTPException(status_code=401, detail=message)

        if not self.verify_password(plain_password=password, hashed_password=user.password_hash):
            logger.warning(f"Попытка авторизации с неверным паролем для пользователя {user.id},"
                           f" переданные данные: {login=} {password=}")
            raise HTTPException(status_code=401, detail="Неверный пароль")

        tokens = TokenService.generate_tokens(user=models.User.from_orm(user))
        logger.info(f"Пользователь {login} успешно авторизован")
        return tokens

    def refresh_tokens(self, refresh_token: str | None) -> models.Tokens:
        """Обновление токенов"""
        logger.debug(f"Попытка обновление токенов с помощью refresh токена: {refresh_token}")
        if not refresh_token:
            logger.warning(f"refresh токен не передан, обновление не выполняется")
            raise HTTPException(status_code=401, detail="Не валидный refresh_token")

        user_data = TokenService.verify_refresh_token(token=refresh_token)
        refresh_token_from_db = TokenService.find_refresh_token(token=refresh_token)

        if not user_data or not refresh_token_from_db:
            logger.debug(f"Не удалось обновить токены, {user_data=}, {refresh_token_from_db=}")
            raise HTTPException(status_code=401, detail="Не удалось обновить токены")

        try:
            user = models.User.from_orm(self._find_user_by_id(user_id=user_data.id))
        except ValidationError as e:
            logger.warning(f"Не удалось получить пользователя по id={user_data.id}: {str(e)}")
            raise HTTPException(status_code=401, detail="Не удалось обновить токены")

        tokens = TokenService.generate_tokens(user=user)

        logger.debug(f"Токены успешно обновлены")
        return tokens

    @staticmethod
    def logout(refresh_token: str | None) -> None:
        """Выход из системы"""
        logger.debug(f"Попытка выхода из системы, refresh_token: {refresh_token} ")
        if not refresh_token:
            logger.warning(f"refresh токен не передан, выход не возможен")
            raise HTTPException(status_code=401, detail="Не валидный refresh_token")

        user_data = TokenService.verify_refresh_token(token=refresh_token)

        TokenService.delete_refresh_token(token=refresh_token)
        logger.info(f"Пользователь '{user_data.login}' выполнен выход из системы")

    def find_user_by_login(self, login: str) -> tables.User | None:
        """Поиск пользователя по login"""
        user = (
            self.session
            .query(tables.User)
            .filter(tables.User.login == login)
            .first()
        )

        return user

    def _find_user_by_id(self, user_id: int) -> tables.User | None:
        """Поиск пользователя по id"""
        user = (
            self.session
            .query(tables.User)
            .filter(tables.User.id == user_id)
            .first()
        )

        return user

    def _create_new_user(self, user_data: models.UserCreate) -> models.User:
        """Создание нового пользователя"""
        new_user = tables.User(
            login=user_data.login,
            password_hash=self.hash_password(user_data.password),
            name=user_data.name,
            surname=user_data.surname
        )
        self.session.add(new_user)
        self.session.commit()

        new_user = models.User.from_orm(new_user)
        logger.info(f"Создан новый пользователь: {new_user}")

        return new_user
