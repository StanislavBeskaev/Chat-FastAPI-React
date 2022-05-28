from fastapi import (
    APIRouter,
    Depends,
    status,
)

from ..dependencies import get_current_user
from ..services.messages import MessageService, MessageData


router = APIRouter(
    prefix='/messages',
    tags=['messages'],
)


@router.get(
    "/",
    response_model=list[MessageData],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)]
)
def get_all_messages(message_service: MessageService = Depends()):
    """Получение всех сообщений"""
    # TODO отправлять сообщения только текущего пользователя
    return message_service.get_many()
