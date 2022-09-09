from fastapi import (
    APIRouter,
    Depends,
    status,
)
from loguru import logger

from backend.dependencies import get_current_user
from backend.services.export import ExportService

router = APIRouter(
    prefix='/data',
    tags=['data'],
)


@router.get(
    "/export",
    status_code=status.HTTP_200_OK # TODO нужна проверка на админа
)
def export_db_data(export_service: ExportService = Depends()):
    """Получение выгрузки данных из базы"""
    logger.info("Запрос выгрузки данных из базы")
    export_service.export_db_data()

    return {"message": "Тут будет экспорт данных"}
