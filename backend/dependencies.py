from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from . import models
from .services.token import TokenService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


def get_current_user(token: str = Depends(oauth2_scheme)) -> models.User:
    return TokenService.verify_access_token(token)
