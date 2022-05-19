from fastapi import APIRouter, Depends, status, UploadFile
from loguru import logger

from .. import models
from ..services.user import UserService
from ..dependencies import get_current_user

router = APIRouter(
    prefix='/user',
    tags=['user'],
)


# TODO документация
# TODO тесты
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


# TODO документация
# TODO тесты
@router.post(
    "/avatar",
    status_code=status.HTTP_201_CREATED
)
def upload_avatar(
        file: UploadFile,
        user_service: UserService = Depends(),
        current_user: models.User = Depends(get_current_user)
):
    """Загрузка аватара пользователя"""
    logger.debug(f"incoming file attrs: {file.__dict__}")

    return {
        "avatar_file": user_service.save_avatar(user=current_user, file=file)
    }


# TODO документация
# TODO тесты
@router.get(
    "/avatar",
    status_code=status.HTTP_200_OK
)
def get_avatar(
        user_service: UserService = Depends(),
        current_user: models.User = Depends(get_current_user),
):
    """Получение имени файла аватара пользователя"""
    logger.debug(f"Запрос получения аватара для пользователя {current_user}")

    return {
        "avatar_file": user_service.get_avatar(user=current_user)
    }
