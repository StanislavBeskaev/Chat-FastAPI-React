from datetime import datetime, timedelta

from jose import jwt
from loguru import logger

from .. import models
from ..settings import get_settings, Settings


class TokenService:
    """Сервис для работы с токенами"""

    @classmethod
    def generate_tokens(cls, user: models.User) -> models.Tokens:
        """Генерация токенов: access и refresh"""
        settings = get_settings()

        tokens = models.Tokens(
            access_token=cls.generate_access_token(user=user, settings=settings),
            refresh_token=cls.generate_refresh_token(user=user, setting=settings)
        )
        logger.debug(f"Для пользователя {user}, сгенерированы токены: {tokens}")
        return tokens

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
