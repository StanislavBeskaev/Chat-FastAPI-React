from fastapi import APIRouter, Depends, status

from backend import models
from backend.api.docs import messages as messages_responses
from backend.dependencies import get_current_user
from backend.metrics import messages as messages_metrics
from backend.services.messages import MessageService


router = APIRouter(
    prefix='/messages',
    tags=['messages'],
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=dict[str, models.ChatMessages],
    responses=messages_responses.get_all_messages_responses,
    summary="Сообщения по всем чатам"
)
def get_all_messages(
    user: models.User = Depends(get_current_user),
    message_service: MessageService = Depends(),
):
    """Получение сообщений по всем чатам текущего пользователя"""
    messages_metrics.GET_ALL_MESSAGES_COUNTER.inc()

    return message_service.get_many(user=user)


@router.get(
    "/{chat_id}",
    status_code=status.HTTP_200_OK,
    response_model=models.ChatMessages,
    responses=messages_responses.get_chat_messages_responses,
    summary="Сообщения чата"
)
def get_chat_messages(
    chat_id: str,
    user: models.User = Depends(get_current_user),
    message_service: MessageService = Depends(),
):
    """Получение сообщений по чату"""
    messages_metrics.GET_CHAT_MESSAGES_COUNTER.inc()

    return message_service.get_chat_messages(user=user, chat_id=chat_id)


@router.put(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
    responses=messages_responses.change_message_text_responses,
    summary="Изменение текста сообщения"
)
def change_message_text(
    message_id: str,
    change_message: models.ChangeMessageText,
    user: models.User = Depends(get_current_user),
    message_service: MessageService = Depends(),
):
    """Изменение текста сообщения"""
    messages_metrics.CHANGE_MESSAGE_TEXT_COUNTER.inc()

    message_service.change_message_text(message_id=message_id, new_text=change_message.text, user=user)

    return {"message": "Текст сообщения изменён"}


@router.delete(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
    responses=messages_responses.delete_message_responses,
    summary="Удаление сообщения"
)
def delete_message(
    message_id: str, user: models.User = Depends(get_current_user), message_service: MessageService = Depends()
):
    """Удаление сообщения"""
    messages_metrics.DELETE_MESSAGE_COUNTER.inc()

    message_service.delete_message(message_id=message_id, user=user)
    return {"message": "Сообщение удалено"}
