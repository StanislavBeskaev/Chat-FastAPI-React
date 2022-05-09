from datetime import datetime, timedelta

from jose import jwt

from .. import models
from ..settings import get_settings


class TokenService:
    """Сервис для работы с токенами"""

    @classmethod
    def generate_tokens(cls, user: models.User) -> models.Tokens:
        now = datetime.utcnow()
        settings = get_settings()

        # TODO подумать как лучше делать payload, включать ли user_data
        #  как вариант вынести отдельным методом создание токена
        payload = {
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(seconds=settings.jwt_access_expires_s),
            "user": user.dict(),
        }
        token = jwt.encode(
            claims=payload,
            key=settings.jwt_access_secret,
            algorithm=settings.jwt_algorithm,
        )

        # TODO refresh_token
        return models.Tokens(access_token=token, refresh_token=token, user=user)