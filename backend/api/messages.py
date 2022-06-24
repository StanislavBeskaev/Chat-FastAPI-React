from fastapi import APIRouter, Depends, status

from backend import models
from backend.dependencies import get_current_user
from backend.services.chat_members import ChatMembersService
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
    status_code=status.HTTP_204_NO_CONTENT
)
def create_new_chat(
        new_chat_data: models.ChatCreate,
        user: models.User = Depends(get_current_user),
        message_service: MessageService = Depends(),
):
    """Создание нового чата"""

    message_service.create_chat(chat_data=new_chat_data, user=user)


@router.put(
    "/chats/{chat_id}",
    status_code=status.HTTP_200_OK
)
def change_chat_name(
        chat_id: str,
        chat_update_data: models.ChatUpdateName,
        user: models.User = Depends(get_current_user),
        message_service: MessageService = Depends(),
):
    """Изменение названия чата"""
    message_service.change_chat_name(
        chat_id=chat_id,
        new_name=chat_update_data.chat_name,
        user=user
    )

    return {"message": "Название чата успешно изменено"}


@router.get(
    "/chat_members/{chat_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
    response_model=list[models.ChatMemberWithOnlineStatus]
)
def get_chat_members(
        chat_id: str,
        chat_members_service: ChatMembersService = Depends()
):
    """Получение списка участников чата с онлайн статусом"""
    return chat_members_service.get_chat_members_with_online_status(chat_id=chat_id)