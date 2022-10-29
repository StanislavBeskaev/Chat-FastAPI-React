from fastapi import APIRouter, Depends, status, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from loguru import logger

from backend import models
from backend.dependencies import get_current_user
from backend.services.db_data import DBDataService
from backend.services.user import UserService

router = APIRouter(
    prefix='/data',
    tags=['data'],
)


@router.get("/export", status_code=status.HTTP_200_OK, summary="Получение архива с данными базы")
def export_db_data(user: models.User = Depends(get_current_user), db_data_service: DBDataService = Depends()):
    """Доступно только для админа"""
    logger.info("Запрос выгрузки данных из базы")
    if not UserService.is_admin(user=user):
        logger.warning("Пользователь запрашивающий выгрузку не админ, отказано")
        raise HTTPException(status_code=403, detail="Не достаточно полномочий")

    logger.debug("Пользователь является админом, выгружаем данные из базы")
    return StreamingResponse(
        content=db_data_service.export_db_data(),
        media_type="application/zip",
        headers={'Content-Disposition': 'attachment; filename=export.zip'},
    )


@router.post("/import", status_code=status.HTTP_200_OK, summary="Замена данных в базе")
def import_db_data(
    file: UploadFile, user: models.User = Depends(get_current_user), db_data_service: DBDataService = Depends()
):
    """Доступно только для админа"""
    logger.info("Запрос импорта данных в базу")
    if not UserService.is_admin(user=user):
        logger.warning("Пользователь импортирующий данные не админ, отказано")
        raise HTTPException(status_code=403, detail="Не достаточно полномочий")

    logger.debug("Пользователь является админом, импортируем данные в базу")
    db_data_service.import_db_data(import_zip_file=file)

    return {"message": "Данные успешно залиты"}
