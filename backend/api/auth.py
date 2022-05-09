from fastapi import (
    APIRouter,
    Depends,
    status,
)

from .. import models
from ..services.auth import AuthService


router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


# TODO документация
@router.post(
    "/registration",
    response_model=models.Tokens,  # TODO токены
    status_code=status.HTTP_201_CREATED
)
def registration(
        user_data: models.UserCreate,
        auth_service: AuthService = Depends()
) -> models.Tokens:
    """Регистрация нового пользователя"""
    return auth_service.registration(user_data=user_data)
