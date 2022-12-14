from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile, status
from fastapi.responses import FileResponse
from loguru import logger

from backend import models
from backend.api.docs import user as user_responses
from backend.dependencies import get_current_user
from backend.metrics import user as user_metrics
from backend.services.files import FilesService
from backend.services.user import UserService

router = APIRouter(
    prefix='/user',
    tags=['user'],
)


@router.put(
    "/change",
    response_model=models.User,
    status_code=status.HTTP_200_OK,
    responses=user_responses.change_user_data_responses,
    summary="Изменение данных пользователя",
)
def change_user_data(
    user_data: models.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    user_service: UserService = Depends(),
):
    """Изменение данных пользователя"""
    user_metrics.CHANGE_USER_DATA_COUNTER.inc()

    updated_user = user_service.change_user_data(user_login=current_user.login, user_data=user_data)
    return updated_user


@router.post(
    "/avatar",
    status_code=status.HTTP_201_CREATED,
    responses=user_responses.upload_avatar_responses,
    summary="Загрузка аватарки",
)
def upload_avatar(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(),
    current_user: models.User = Depends(get_current_user),
    files_service: FilesService = Depends(),
):
    """Загрузка аватара пользователя"""
    user_metrics.UPLOAD_AVATAR_COUNTER.inc()

    logger.debug(f"incoming file attrs: {file.__dict__}")
    background_tasks.add_task(files_service.delete_not_used_avatar_files)

    return {"avatar_file": user_service.save_avatar(user=current_user, file=file)}


@router.get(
    "/avatar_file/{login}",
    status_code=status.HTTP_200_OK,
    responses=user_responses.get_login_avatar_file_responses,
    summary="Файл аватара пользователя",
)
def get_login_avatar_file(login: str, user_service: UserService = Depends()):
    """Получение файла аватара пользователя по логину"""
    user_metrics.GET_LOGIN_AVATAR_FILE_COUNTER.inc()

    return FileResponse(path=user_service.get_avatar_file_path_by_login(login=login), media_type="image/png")


@router.get(
    "/avatar_file_name/{login}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
    responses=user_responses.get_login_avatar_filename_responses,
    summary="Название файла аватара пользователя",
)
def get_login_avatar_filename(login: str, user_service: UserService = Depends()):
    """Получение названия файла аватара пользователя по логину"""
    user_metrics.GET_LOGIN_AVATAR_FILENAME_COUNTER.inc()

    logger.debug(f"Запрос получения наименования аватара для пользователя {login}")
    return {"avatar_file": user_service.get_avatar_by_login(login=login)}


@router.get(
    "/info/{login}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
    response_model=models.User,
    responses=user_responses.get_user_info_responses,
    summary="Информация о пользователе",
)
def get_user_info(login: str, user_service: UserService = Depends()):
    """Получение информации о пользователе по логину"""
    user_metrics.GET_USER_INFO_COUNTER.inc()

    logger.debug(f"Запрос получения информации о пользователе: {login}")
    return user_service.get_user_info(login=login)
