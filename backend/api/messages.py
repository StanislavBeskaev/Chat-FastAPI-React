from fastapi import (
    APIRouter,
    Depends,
    status,
)

from ..dependencies import get_current_user
from ..services.messages import MessageService


router = APIRouter(
    prefix='/messages',
    tags=['messages'],
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)]
)
def get_all_messages(message_service: MessageService = Depends()):
    """Получение всех сообщений"""
    # TODO отправлять сообщения только текущего пользователя
    return message_service.get_many()
