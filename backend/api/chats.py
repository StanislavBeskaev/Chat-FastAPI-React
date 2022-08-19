from fastapi import APIRouter, Depends, status

from backend import models
from backend.dependencies import get_current_user
from backend.metrics import chats as chats_metrics
from backend.services.chat import ChatService


router = APIRouter(
    prefix='/chats',
    tags=['chats'],
)


# TODO Документация
@router.post(
    "/",
    status_code=status.HTTP_200_OK
)
def create_new_chat(
        new_chat_data: models.ChatCreate,
        user: models.User = Depends(get_current_user),
        chat_service: ChatService = Depends(),
):
    """Создание нового чата"""
    chats_metrics.CREATE_NEW_CHAT_COUNTER.inc()

    chat_service.create_chat(chat_data=new_chat_data, user=user)


# TODO Документация
@router.put(
    "/{chat_id}",
    status_code=status.HTTP_200_OK
)
def change_chat_name(
        chat_id: str,
        chat_update_data: models.ChatUpdateName,
        user: models.User = Depends(get_current_user),
        chat_service: ChatService = Depends(),
):
    """Изменение названия чата"""
    chats_metrics.CHANGE_CHAT_NAME_COUNTER.inc()

    chat_service.change_chat_name(
        chat_id=chat_id,
        new_name=chat_update_data.chat_name,
        user=user
    )

    return {"message": "Название чата успешно изменено"}
