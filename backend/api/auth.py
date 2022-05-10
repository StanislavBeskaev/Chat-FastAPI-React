from fastapi import APIRouter, Depends, Response, status, Cookie
from fastapi.security import OAuth2PasswordRequestForm

from .. import models
from ..services.auth import AuthService
from ..settings import get_settings, Settings


router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


# TODO документация
# TODO тесты
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
        key="refreshToken",
        value=tokens.refresh_token,
        expires=settings.jwt_refresh_expires_s,
        httponly=True
    )
    return tokens


# TODO документация
# TODO тесты
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
        key="refreshToken",
        value=tokens.refresh_token,
        expires=settings.jwt_refresh_expires_s,
        httponly=True
    )
    return tokens


# TODO документация
# TODO тесты
@router.get(
    "/refresh",
    response_model=models.Tokens,
    status_code=status.HTTP_200_OK
)
def refresh_tokens(
    response: Response,
    auth_service: AuthService = Depends(),
    refresh_token: str = Cookie(None, alias="refreshToken"),
    settings: Settings = Depends(get_settings)
) -> models.Tokens:
    """Обновление токенов"""
    tokens = auth_service.refresh_tokens(refresh_token=refresh_token)
    response.set_cookie(
        key="refreshToken",
        value=tokens.refresh_token,
        expires=settings.jwt_refresh_expires_s,
        httponly=True
    )
    return tokens
