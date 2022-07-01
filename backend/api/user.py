from fastapi import APIRouter, Depends, status, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from loguru import logger

from backend import models
from backend.services.files import FilesService
from backend.services.user import UserService
from backend.dependencies import get_current_user

router = APIRouter(
    prefix='/user',
    tags=['user'],
)


# TODO документация
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
        background_tasks: BackgroundTasks,
        user_service: UserService = Depends(),
        current_user: models.User = Depends(get_current_user),
        files_service: FilesService = Depends()
):
    """Загрузка аватара пользователя"""
    logger.debug(f"incoming file attrs: {file.__dict__}")
    background_tasks.add_task(files_service.delete_not_used_avatar_files)

    return {
        "avatar_file": user_service.save_avatar(user=current_user, file=file)
    }


# TODO документация
# TODO тесты как-то
@router.get(
    "/avatar_file/{login}",
    status_code=status.HTTP_200_OK,
)
def get_login_avatar_file(
        login: str,
        user_service: UserService = Depends()
):
    """Получение файла аватара пользователя по логину"""

    return FileResponse(path=user_service.get_avatar_file_path_by_login(login=login), media_type="image/png")


# TODO документация
@router.get(
    "/info/{login}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
    response_model=models.User
)
def get_user_info(
        login: str,
        user_service: UserService = Depends()
):
    """Получение информации о пользователе по логину"""
    logger.debug(f"Запрос получения информации о пользователе: {login}")

    return user_service.get_user_info(login=login)
