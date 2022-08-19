from fastapi import APIRouter, Depends, Response, status, Cookie, Request
from fastapi.security import OAuth2PasswordRequestForm

from backend import models
from backend.metrics import auth as auth_metrics
from backend.services.auth import AuthService
from backend.settings import get_settings, Settings


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
        request: Request,
        response: Response,
        user_data: models.UserCreate,
        auth_service: AuthService = Depends(),
        settings: Settings = Depends(get_settings)
) -> models.Tokens:
    """Регистрация нового пользователя"""
    auth_metrics.REGISTRATION_COUNTER.inc()

    tokens = auth_service.register_new_user(
        user_data=user_data,
        user_agent=request.headers.get('user-agent')
    )
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
        request: Request,
        response: Response,
        user_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: AuthService = Depends(),
        settings: Settings = Depends(get_settings)
) -> models.Tokens:
    """Авторизация пользователя"""
    auth_metrics.LOGIN_COUNTER.inc()

    tokens = auth_service.login_user(
        login=user_data.username,
        password=user_data.password,
        user_agent=request.headers.get('user-agent')
    )
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
    auth_metrics.REFRESH_TOKENS_COUNTER.inc()

    tokens = auth_service.refresh_tokens(
        refresh_token=refresh_token,
        user_agent=request.headers.get('user-agent')
    )
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
        request: Request,
        response: Response,
        auth_service: AuthService = Depends(),
        refresh_token: str = Cookie(None, alias=REFRESH_TOKEN_COOKIE_KEY),
):
    """Выход из системы"""
    auth_metrics.LOGOUT_COUNTER.inc()

    auth_service.logout(
        refresh_token=refresh_token,
        user_agent=request.headers.get('user-agent')
    )
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE_KEY
    )

    return {"message": "Выход из системы выполнен"}
