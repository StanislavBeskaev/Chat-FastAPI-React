from fastapi import APIRouter, Depends, Response, status

from .. import models
from ..services.auth import AuthService
from ..settings import get_settings


router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


# TODO документация
@router.post(
    "/registration",
    response_model=models.Tokens,
    status_code=status.HTTP_201_CREATED
)
def registration(
        response: Response,
        user_data: models.UserCreate,
        auth_service: AuthService = Depends()
) -> models.Tokens:
    """Регистрация нового пользователя"""
    settings = get_settings()
    tokens = auth_service.register_new_user(user_data=user_data)
    response.set_cookie(
        key="refreshToken",
        value=tokens.refresh_token,
        expires=settings.jwt_refresh_expires_s,
        httponly=True
    )
    return tokens
