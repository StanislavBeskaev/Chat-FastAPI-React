from fastapi import (
    APIRouter,
    Depends,
    status,
)

from ..services.messages import MessageService, MessageData


router = APIRouter(
    prefix='/messages',
    tags=['messages'],
)


@router.get(
    "/",
    response_model=list[MessageData],
    status_code=status.HTTP_200_OK
)
def get_all_messages(message_service: MessageService = Depends()):
    """Получение всех сообщений"""
    return message_service.get_many()
