from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from backend import models
from backend.services.token import TokenService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')


def get_current_user(token: str = Depends(oauth2_scheme), token_service: TokenService = Depends()) -> models.User:
    """Зависимость для проверки авторизации пользователя по JWT"""
    return token_service.verify_access_token(token)
