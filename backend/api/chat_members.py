from fastapi import APIRouter, Depends, status

from backend import models
from backend.dependencies import get_current_user
from backend.services.chat_members import ChatMembersService


router = APIRouter(
    prefix='/chat_members',
    tags=['chat_members'],
)


# TODO Документация
# TODO Тесты
@router.get(
    "/{chat_id}",
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


# TODO Документация
@router.post(
    "/{chat_id}",
    status_code=status.HTTP_201_CREATED
)
def add_chat_member(
        chat_id: str,
        chat_member: models.ChatMember,
        chat_members_service: ChatMembersService = Depends(),
        current_user: models.User = Depends(get_current_user)
):
    """Добавление участника к чату"""
    chat_members_service.add_login_to_chat(
        action_user=current_user,
        login=chat_member.login,
        chat_id=chat_id
    )

    return {"message": f"Пользователь {chat_member.login} добавлен к чату: {chat_id}"}


# TODO Документация
# TODO Тесты
@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_200_OK
)
def delete_chat_member(
        chat_id: str,
        chat_member: models.ChatMember,
        chat_members_service: ChatMembersService = Depends(),
        current_user: models.User = Depends(get_current_user)
):
    """Удаление участника из чата"""
    chat_members_service.delete_login_from_chat(
        action_user=current_user,
        login=chat_member.login,
        chat_id=chat_id
    )

    return {"message": f"Пользователь {chat_member.login} удалён из чата: {chat_id}"}
