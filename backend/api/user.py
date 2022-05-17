import os

from fastapi import APIRouter, Depends, status, UploadFile
from loguru import logger

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


@router.post(
    "/avatar",
    status_code=status.HTTP_201_CREATED
)
def upload_avatar(file: UploadFile):
    logger.debug(f"incoming file attrs: {file.__dict__}")

    return {"filepath": write_binary_file(file)}


# TODO вынести в сервис работу с файлами, потом сделать сохранение в minio S3

FILES_FOLDER = "files"


def check_files_folder(func):
    def wrapper(*args, **kwargs):
        if not os.path.exists(FILES_FOLDER):
            logger.debug(f"Создана папка под файлы {FILES_FOLDER}")
            os.mkdir(FILES_FOLDER)

        return func(*args, **kwargs)

    return wrapper


@check_files_folder
def write_binary_file(file: UploadFile) -> str:
    file_path = get_file_path(file.filename)
    with open(file_path, mode="wb") as writable_file:
        writable_file.write(file.file.read())

    logger.debug(f"Бинарный файл {file.filename} записан в {file_path}")

    return file_path


def get_file_path(file_name: str) -> str:
    return os.path.join(FILES_FOLDER, file_name)
