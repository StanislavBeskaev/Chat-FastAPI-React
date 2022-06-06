from fastapi import APIRouter, Depends, Response, status, Cookie, Request
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger

from .. import models
from ..services.auth import AuthService
from ..settings import get_settings, Settings


router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)

REFRESH_TOKEN_COOKIE_KEY = "refreshToken"


# TODO документация
@router.post(
    "/registration",
    response_model=models.Tokens,
    status_code=status.HTTP_201_CREATED
)
def registration(
        response: Response,
        user_data: models.UserCreate,
        auth_service: AuthService = Depends(),
        settings: Settings = Depends(get_settings)
) -> models.Tokens:
    """Регистрация нового пользователя"""
    tokens = auth_service.register_new_user(user_data=user_data)
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_KEY,
        value=tokens.refresh_token,
        expires=settings.jwt_refresh_expires_s,
        httponly=True
    )
    return tokens


# TODO документация
@router.post(
    "/login",
    response_model=models.Tokens,
    status_code=status.HTTP_200_OK
)
def login(
        response: Response,
        user_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: AuthService = Depends(),
        settings: Settings = Depends(get_settings)
) -> models.Tokens:
    """Авторизация пользователя"""
    tokens = auth_service.login_user(login=user_data.username, password=user_data.password)
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_KEY,
        value=tokens.refresh_token,
        expires=settings.jwt_refresh_expires_s,
        httponly=True
    )
    return tokens


# TODO документация
@router.get(
    "/refresh",
    response_model=models.Tokens,
    status_code=status.HTTP_200_OK
)
def refresh_tokens(
        request: Request,
        response: Response,
        auth_service: AuthService = Depends(),
        refresh_token: str = Cookie(None, alias=REFRESH_TOKEN_COOKIE_KEY),
        settings: Settings = Depends(get_settings)
) -> models.Tokens:
    """Обновление токенов"""
    logger.debug(f"{request.__dict__}")

    tokens = auth_service.refresh_tokens(refresh_token=refresh_token)
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_KEY,
        value=tokens.refresh_token,
        expires=settings.jwt_refresh_expires_s,
        httponly=True
    )
    return tokens


# TODO документация
@router.post(
    "/logout",
    status_code=status.HTTP_200_OK
)
def logout(
        response: Response,
        auth_service: AuthService = Depends(),
        refresh_token: str = Cookie(None, alias=REFRESH_TOKEN_COOKIE_KEY),
):
    """Выход из системы"""
    auth_service.logout(refresh_token=refresh_token)
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE_KEY
    )

    return {"message": "Выход из системы выполнен"}
