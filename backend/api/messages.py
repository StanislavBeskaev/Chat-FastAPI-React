from fastapi import APIRouter, Depends, status

from backend import models
from backend.dependencies import get_current_user
from backend.services.messages import MessageService


router = APIRouter(
    prefix='/messages',
    tags=['messages'],
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=dict[str, models.ChatMessages]
)
def get_all_messages(
        user: models.User = Depends(get_current_user),
        message_service: MessageService = Depends(),
):
    """Получение сообщений текущего пользователя"""

    return message_service.get_many(user=user)
