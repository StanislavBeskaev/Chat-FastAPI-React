from fastapi import APIRouter, Depends, status

from .. import models
from ..services.user import UserService
from ..dependencies import get_current_user

router = APIRouter(
    prefix='/user',
    tags=['user'],
)


@router.put(
    "/change",
    response_model=models.User,
    status_code=status.HTTP_200_OK
)
def change_user_data(
        user_data: models.UserUpdate,
        current_user: models.User = Depends(get_current_user),
        user_service: UserService = Depends()
):
    """Изменение данных пользователя"""
    updated_user = user_service.change_user_data(user_login=current_user.login, user_data=user_data)
    return updated_user
