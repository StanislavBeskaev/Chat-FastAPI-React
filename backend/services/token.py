from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import JWTError, jwt
from loguru import logger
from pydantic import ValidationError

from backend import models, tables
from backend.services import BaseService
from backend.settings import Settings, get_settings

USER_JWT_KEY = "user"


class TokenService(BaseService):
    """Сервис для работы с токенами"""

    def generate_tokens(self, user: models.User, user_agent: str) -> models.Tokens:
        """Генерация токенов: access и refresh"""
        settings = get_settings()

        tokens = models.Tokens(
            access_token=self.generate_access_token(user=user, settings=settings),
            refresh_token=self.generate_refresh_token(user=user, setting=settings),
            user=user,
        )
        logger.debug(
            f"Для пользователя {user}, {user_agent=},"
            f" сгенерированы токены: {tokens.access_token=}, {tokens.refresh_token=}"
        )
        self.save_refresh_token_to_db(user_id=user.id, refresh_token=tokens.refresh_token, user_agent=user_agent)

        return tokens

    def save_refresh_token_to_db(self, user_id: int, refresh_token: str, user_agent: str) -> tables.RefreshToken:
        """Сохранение refresh токена для пользователя с id=user_id и приложением=user_agent в базу данных"""
        logger.debug(f"Пользователь {user_id}, запрос на сохранение refresh токена в базу: '{refresh_token}'")
        token = self._db_facade.find_refresh_token_by_user(user_id=user_id, user_agent=user_agent)
        if token:
            logger.debug(f"Для пользователя {user_id} уже существует refresh_token, обновляем")
            self._db_facade.update_refresh_token(token=token, new_refresh_token=refresh_token)
        else:
            logger.debug(f"Для пользователя {user_id} не было refresh_token в базе, создаём новый")
            token = self._db_facade.create_refresh_token(
                user_id=user_id, refresh_token=refresh_token, user_agent=user_agent
            )

        logger.info(f"Для пользователя {user_id} {user_agent=} в базу сохранён refresh_token: {refresh_token}")
        return token

    def generate_access_token(self, user: models.User, settings: Settings) -> str:
        """Генерация токена доступа"""
        return self._generate_token(
            user=user,
            duration=settings.jwt_access_expires_s,
            secret_key=settings.jwt_access_secret,
            algorithm=settings.jwt_algorithm,
            token_kind="access",
        )

    def generate_refresh_token(self, user: models.User, setting: Settings) -> str:
        """Генерация refresh токена"""
        return self._generate_token(
            user=user,
            duration=setting.jwt_refresh_expires_s,
            secret_key=setting.jwt_refresh_secret,
            algorithm=setting.jwt_algorithm,
            token_kind="refresh",
        )

    @staticmethod
    def _generate_token(user: models.User, duration: int, secret_key: str, algorithm: str, token_kind: str) -> str:
        """Генерация токена"""
        now = datetime.utcnow()
        payload = {
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(seconds=duration),
            "kind": token_kind,
            USER_JWT_KEY: user.dict(),
        }
        token = jwt.encode(claims=payload, key=secret_key, algorithm=algorithm)

        return token

    @staticmethod
    def verify_access_token(token: str) -> models.User:
        """Проверка токена доступа"""
        logger.debug(f"Проверяем access_token: {token}")
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Не валидный токен доступа',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        try:
            settings = get_settings()
            payload = jwt.decode(token=token, key=settings.jwt_access_secret, algorithms=[settings.jwt_algorithm])
        except JWTError:
            logger.warning("access_token не валидный")
            raise exception from None

        logger.debug(f"{payload=}")
        user_data = payload.get(USER_JWT_KEY)

        try:
            user = models.User.parse_obj(user_data)
        except ValidationError as e:
            logger.debug(f"Сработал ValidationError: {str(e)}")
            raise exception from None

        logger.debug(f"Верный access_token: {token}")
        return user

    @staticmethod
    def verify_refresh_token(token) -> models.User:
        """Проверка refresh токена"""
        logger.debug(f"Проверяем refresh токен: {token}")
        settings = get_settings()
        exception = HTTPException(status_code=401, detail="Не валидный refresh_token")
        try:
            payload = jwt.decode(token=token, key=settings.jwt_refresh_secret, algorithms=[settings.jwt_algorithm])
        except JWTError:
            logger.warning("refresh токен не валидный")
            raise exception from None

        logger.debug(f"{payload=}")
        user_data = payload.get(USER_JWT_KEY)

        try:
            user = models.User.parse_obj(user_data)
        except ValidationError as e:
            logger.debug(f"Сработал ValidationError: {str(e)}")
            raise exception from None

        logger.debug(f"Верный refresh_token: {token}")
        return user

    def delete_refresh_token(self, token: str, user_agent: str) -> None:
        """Удаление refresh токена для user_agent"""
        self._db_facade.delete_refresh_token(token=token, user_agent=user_agent)
        logger.debug(f"Из базы удалён refresh_token: {token}")
