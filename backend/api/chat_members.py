from fastapi import APIRouter, Depends, status

from backend import models
from backend.api.docs import chat_members as chat_members_responses
from backend.dependencies import get_current_user
from backend.metrics import chat_members as chat_members_metrics
from backend.services.chat_members import ChatMembersService


router = APIRouter(
    prefix='/chat_members',
    tags=['chat_members'],
)


@router.get(
    "/{chat_id}",
    status_code=status.HTTP_200_OK,
    response_model=list[models.ChatMemberWithOnlineStatus],
    responses=chat_members_responses.get_chat_members_responses
)
def get_chat_members(
        chat_id: str,
        chat_members_service: ChatMembersService = Depends(),
        current_user: models.User = Depends(get_current_user)
):
    """Получение списка участников чата с онлайн статусом"""
    chat_members_metrics.GET_CHAT_MEMBERS_COUNTER.inc()

    return chat_members_service.get_chat_members_with_online_status(chat_id=chat_id, user=current_user)


@router.post(
    "/{chat_id}",
    status_code=status.HTTP_201_CREATED,
    responses=chat_members_responses.add_chat_member_responses
)
def add_chat_member(
        chat_id: str,
        chat_member: models.ChatMember,
        chat_members_service: ChatMembersService = Depends(),
        current_user: models.User = Depends(get_current_user)
):
    """Добавление участника к чату"""
    chat_members_metrics.ADD_CHAT_MEMBER_COUNTER.inc()

    chat_members_service.add_login_to_chat(
        action_user=current_user,
        login=chat_member.login,
        chat_id=chat_id
    )

    return {"message": f"Пользователь {chat_member.login} добавлен к чату: {chat_id}"}


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_200_OK,
    responses=chat_members_responses.delete_chat_member_responses
)
def delete_chat_member(
        chat_id: str,
        chat_member: models.ChatMember,
        chat_members_service: ChatMembersService = Depends(),
        current_user: models.User = Depends(get_current_user)
):
    """Удаление участника из чата"""
    chat_members_metrics.DELETE_CHAT_MEMBERS_COUNTER.inc()

    chat_members_service.delete_login_from_chat(
        action_user=current_user,
        login=chat_member.login,
        chat_id=chat_id
    )

    return {"message": f"Пользователь {chat_member.login} удалён из чата: {chat_id}"}
