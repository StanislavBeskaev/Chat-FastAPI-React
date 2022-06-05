from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from . import models
from .services.token import TokenService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')


def get_current_user(token: str = Depends(oauth2_scheme), token_service: TokenService = Depends()) -> models.User:
    return token_service.verify_access_token(token)
