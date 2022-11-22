from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from backend import models
from backend.api.docs import auth as auth_responses
from backend.metrics import auth as auth_metrics
from backend.services.auth import AuthService
from backend.settings import Settings, get_settings

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)

REFRESH_TOKEN_COOKIE_KEY = "refreshToken"


@router.post(
    "/registration",
    response_model=models.Tokens,
    status_code=status.HTTP_201_CREATED,
    responses=auth_responses.registration_responses,
    summary="Регистрация",
)
def registration(
    request: Request,
    response: Response,
    user_data: models.UserCreate,
    auth_service: AuthService = Depends(),
    settings: Settings = Depends(get_settings),
) -> models.Tokens:
    """Регистрация нового пользователя"""
    auth_metrics.REGISTRATION_COUNTER.inc()

    tokens = auth_service.register_new_user(user_data=user_data, user_agent=request.headers.get('user-agent'))
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_KEY, value=tokens.refresh_token, expires=settings.jwt_refresh_expires_s, httponly=True
    )
    return tokens


@router.post(
    "/login",
    response_model=models.Tokens,
    status_code=status.HTTP_200_OK,
    responses=auth_responses.login_responses,
    summary="Вход в систему",
)
def login(
    request: Request,
    response: Response,
    user_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(),
    settings: Settings = Depends(get_settings),
) -> models.Tokens:
    """Авторизация пользователя"""
    auth_metrics.LOGIN_COUNTER.inc()

    tokens = auth_service.login_user(
        login=user_data.username, password=user_data.password, user_agent=request.headers.get('user-agent')
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_KEY, value=tokens.refresh_token, expires=settings.jwt_refresh_expires_s, httponly=True
    )
    return tokens


@router.get(
    "/refresh",
    response_model=models.Tokens,
    status_code=status.HTTP_200_OK,
    responses=auth_responses.refresh_responses,
    summary="Обновление токенов доступа",
)
def refresh_tokens(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(),
    refresh_token: str = Cookie(None, alias=REFRESH_TOKEN_COOKIE_KEY),
    settings: Settings = Depends(get_settings),
) -> models.Tokens:
    """Обновление токенов"""
    auth_metrics.REFRESH_TOKENS_COUNTER.inc()

    tokens = auth_service.refresh_tokens(refresh_token=refresh_token, user_agent=request.headers.get('user-agent'))
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_KEY, value=tokens.refresh_token, expires=settings.jwt_refresh_expires_s, httponly=True
    )
    return tokens


@router.post(
    "/logout", status_code=status.HTTP_200_OK, responses=auth_responses.logout_responses, summary="Выход из системы"
)
def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(),
    refresh_token: str = Cookie(None, alias=REFRESH_TOKEN_COOKIE_KEY),
):
    """Выход из системы"""
    auth_metrics.LOGOUT_COUNTER.inc()

    auth_service.logout(refresh_token=refresh_token, user_agent=request.headers.get('user-agent'))
    response.delete_cookie(key=REFRESH_TOKEN_COOKIE_KEY)

    return {"message": "Выход из системы выполнен"}
