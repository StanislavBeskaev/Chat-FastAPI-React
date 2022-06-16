from fastapi import (
    APIRouter,
    Depends,
    status,
)

from .. import models
from ..dependencies import get_current_user
from ..services.messages import MessageService, Chat


router = APIRouter(
    prefix='/messages',
    tags=['messages'],
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=dict[str, Chat]
)
def get_all_messages(
        user: models.User = Depends(get_current_user),
        message_service: MessageService = Depends(),
):
    """Получение сообщений текущего пользователя"""
    # TODO отправлять сообщения только текущего пользователя
    return message_service.get_many(user=user)
