from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import jwt, JWTError
from loguru import logger
from pydantic import ValidationError

from .. import models, tables
from ..database import get_session
from ..settings import get_settings, Settings


class TokenService:
    """Сервис для работы с токенами"""
    session = next(get_session())

    @classmethod
    def generate_tokens(cls, user: models.User) -> models.Tokens:
        """Генерация токенов: access и refresh"""
        settings = get_settings()

        tokens = models.Tokens(
            access_token=cls.generate_access_token(user=user, settings=settings),
            refresh_token=cls.generate_refresh_token(user=user, setting=settings),
            user=user
        )
        logger.debug(f"Для пользователя {user}, сгенерированы токены: {tokens.access_token=}, {tokens.refresh_token=}")
        cls.save_refresh_token_to_db(user_id=user.id, refresh_token=tokens.refresh_token)

        return tokens

    @classmethod
    def save_refresh_token_to_db(cls, user_id: int, refresh_token: str) -> tables.RefreshToken:
        """Сохранение refresh токена для пользователя с id=user_id в базу данных"""
        logger.debug(f"Пользователь {user_id}, запрос на сохранение refresh токена в базу: '{refresh_token}'")
        token = cls._find_refresh_token_by_user_id(user_id=user_id)
        if token:
            logger.debug(f"Для пользователя {user_id} уже существует refresh_token, обновляем")
            token.refresh_token = refresh_token
        else:
            logger.debug(f"Для пользователя {user_id} не было refresh_token в базе, создаём новый")
            token = tables.RefreshToken(
                user=user_id,
                refresh_token=refresh_token
            )

        cls.session.add(token)
        cls.session.commit()
        logger.info(f"Для пользователя {user_id} в базу сохранён refresh_token: {refresh_token}")
        return token

    @classmethod
    def _find_refresh_token_by_user_id(cls, user_id: int) -> tables.RefreshToken | None:
        refresh_token = (
            cls.session
            .query(tables.RefreshToken)
            .filter(tables.RefreshToken.user == user_id)
            .first()
        )

        return refresh_token

    @classmethod
    def find_refresh_token(cls, token: str) -> tables.RefreshToken | None:
        refresh_token = (
            cls.session
            .query(tables.RefreshToken)
            .filter(tables.RefreshToken.refresh_token == token)
            .first()
        )

        return refresh_token

    @classmethod
    def generate_access_token(cls, user: models.User, settings: Settings) -> str:
        """Генерация токена доступа"""
        return cls._generate_token(
            user=user,
            duration=settings.jwt_access_expires_s,
            secret_key=settings.jwt_access_secret,
            algorithm=settings.jwt_algorithm,
            token_kind="access"
        )

    @classmethod
    def generate_refresh_token(cls, user: models.User, setting: Settings) -> str:
        """Генерация refresh токена"""
        return cls._generate_token(
            user=user,
            duration=setting.jwt_refresh_expires_s,
            secret_key=setting.jwt_refresh_secret,
            algorithm=setting.jwt_algorithm,
            token_kind="refresh"
        )

    # TODO посмотреть, может нужен общий payload
    @classmethod
    def _generate_token(cls, user: models.User, duration: int, secret_key: str, algorithm: str, token_kind: str) -> str:
        """Генерация токена"""
        now = datetime.utcnow()
        payload = {
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(seconds=duration),
            "kind": token_kind,
            "user": user.dict(),
        }
        token = jwt.encode(
            claims=payload,
            key=secret_key,
            algorithm=algorithm
        )

        return token

    @classmethod
    def verify_access_token(cls, token: str) -> models.User:
        """Проверка токена доступа"""
        logger.debug(f"Проверяем access_token: {token}")
        settings = get_settings()
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Не валидный токен доступа',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        try:
            payload = jwt.decode(
                token=token,
                key=settings.jwt_access_secret,
                algorithms=[settings.jwt_algorithm]
            )
        except JWTError:
            logger.warning(f"access_token не валидный")
            raise exception from None

        logger.debug(f"{payload=}")
        user_data = payload.get('user')

        try:
            user = models.User.parse_obj(user_data)
        except ValidationError as e:
            logger.debug(f"Сработал ValidationError: {str(e)}")
            raise exception from None

        logger.debug(f"Верный access_token: {token}")
        return user

    @classmethod
    def verify_refresh_token(cls, token) -> models.User:
        """Проверка refresh токена"""
        logger.debug(f"Проверяем refresh токен: {token}")
        settings = get_settings()
        exception = HTTPException(status_code=401, detail="Не валидный refresh_token")
        try:
            payload = jwt.decode(
                token=token,
                key=settings.jwt_refresh_secret,
                algorithms=[settings.jwt_algorithm]
            )
        except JWTError:
            logger.warning(f"refresh токен не валидный")
            raise exception from None

        logger.debug(f"{payload=}")
        user_data = payload.get('user')

        try:
            user = models.User.parse_obj(user_data)
        except ValidationError as e:
            logger.debug(f"Сработал ValidationError: {str(e)}")
            raise exception from None

        logger.debug(f"Верный refresh_token: {token}")
        return user

    @classmethod
    def delete_refresh_token(cls, token: str) -> None:
        refresh_token = cls.find_refresh_token(token=token)
        cls.session.delete(refresh_token)
        cls.session.commit()
        logger.debug(f"Из базы удалён refresh_token: {token}")
