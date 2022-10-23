from fastapi import APIRouter, Depends, status

from backend import models
from backend.api.docs import chats as chats_responses
from backend.dependencies import get_current_user
from backend.metrics import chats as chats_metrics
from backend.services.chat import ChatService


router = APIRouter(
    prefix='/chats',
    tags=['chats'],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses=chats_responses.create_new_chat_responses
)
def create_new_chat(
        new_chat_data: models.ChatCreate,
        user: models.User = Depends(get_current_user),
        chat_service: ChatService = Depends(),
):
    """Создание нового чата"""
    chats_metrics.CREATE_NEW_CHAT_COUNTER.inc()

    chat_service.create_chat(chat_data=new_chat_data, user=user)

    return {"message": f"Чат {new_chat_data.chat_name} успешно создан"}


@router.put(
    "/{chat_id}",
    status_code=status.HTTP_200_OK,
    responses=chats_responses.change_chat_name_responses
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


@router.get(
    "/try_leave/{chat_id}",
    status_code=status.HTTP_200_OK,
    responses=chats_responses.try_leave_chat_responses
)
def try_leave_chat(
        chat_id: str,
        user: models.User = Depends(get_current_user),
        chat_service: ChatService = Depends()
):
    """Попытка выйти из чата, получение предупредительного сообщения"""
    # TODO настроить Grafana под новую метрику
    chats_metrics.TRY_LEAVE_CHAT_COUNTER.inc()

    warning_message = chat_service.try_leave_chat(chat_id=chat_id, user=user)

    return {"message": warning_message}


# TODO тесты
# TODO документация
# TODO Grafana
@router.post(
    "leave_chat/{chat_id}",
    status_code=status.HTTP_200_OK
)
def leave_chat(
        chat_id: str,
        user: models.User = Depends(get_current_user),
        chat_service: ChatService = Depends()
):
    """Выход пользователя из чата"""
    chats_metrics.LEAVE_CHAT_COUNTER.inc()

    chat_service.leave_chat(chat_id=chat_id, user=user)
    return {"message": "Вы вышли из чата"}
