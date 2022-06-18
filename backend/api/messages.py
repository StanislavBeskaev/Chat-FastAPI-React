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


@router.post(
    "/chats/",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)]
)
def create_new_chat(
    message_service: MessageService = Depends(),
):
    """Создание нового чата"""
    # TODO получение данных от пользователя
    new_chat_data = models.ChatCreate(
        chat_name="Супер чат!",
        members=["admin", "test", "new"]
    )

    message_service.create_chat(chat_data=new_chat_data)
