from fastapi import APIRouter, Depends, status

from backend import models
from backend.dependencies import get_current_user
from backend.services.messages import MessageService


router = APIRouter(
    prefix='/messages',
    tags=['messages'],
)


# TODO Документация
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


# TODO Документация
@router.get(
    "/{chat_id}",
    status_code=status.HTTP_200_OK,
    response_model=models.ChatMessages
)
def get_chat_messages(
        chat_id: str,
        user: models.User = Depends(get_current_user),
        message_service: MessageService = Depends(),
):
    """Получение сообщений по чату"""

    return message_service.get_chat_messages(user=user, chat_id=chat_id)


# TODO Документация
@router.put(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
)
def change_message_text(
        message_id: str,
        change_message: models.ChangeMessageText,
        user: models.User = Depends(get_current_user),
        message_service: MessageService = Depends()
):
    """Изменение текста сообщения"""

    message_service.change_message_text(
        message_id=message_id,
        new_text=change_message.text,
        user=user
    )


# TODO Документация
@router.delete(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
)
def delete_message(
    message_id: str,
    user: models.User = Depends(get_current_user),
    message_service: MessageService = Depends()
):
    """Удаление сообщения"""

    message_service.delete_message(message_id=message_id, user=user)
