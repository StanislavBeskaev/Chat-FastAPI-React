from fastapi import status

from backend.core.docs import DocResponseExample, StatusCodeDocResponseExample, DocResponses
from backend.models import ChatMemberWithOnlineStatus


_success_get_chat_members_example = [
    ChatMemberWithOnlineStatus(login="admin", is_online=True).dict(),
    ChatMemberWithOnlineStatus(login="user1", is_online=True).dict(),
    ChatMemberWithOnlineStatus(login="user2", is_online=False).dict(),
    ChatMemberWithOnlineStatus(login="user3", is_online=True).dict(),
]
_user_not_chat_member_example = {"detail": "Вы не участник чата chat_id"}
_chat_not_exist_example = {"detail": "Чата с id chat_id не существует"}

_not_chat_member_status_code_response_example = StatusCodeDocResponseExample(
    status_code=status.HTTP_403_FORBIDDEN,
    response_example=DocResponseExample(
        description="Запрос участников чата от не участника чата",
        example=_user_not_chat_member_example
    )
)

_success_add_chat_member_example = {"message": f"Пользователь login добавлен к чату: chat_id"}
_not_exist_user_example = {"detail": "Пользователя с логином login не существует"}

_success_delete_chat_member_example = {"message": f"Пользователь login удалён из чата: chat_id"}
_user_is_not_chat_creator_example = {"detail": "Только создатель может удалять из чата"}
_login_is_not_chat_member_example = {"detail": "Пользователя login нет в чате"}

get_chat_members_responses = DocResponses.get_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешное получение списка участников чата",
                example=_success_get_chat_members_example
            )
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_403_FORBIDDEN,
            response_example=DocResponseExample(
                description="Запрос участников чата от не участника чата",
                example=_user_not_chat_member_example
            )
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_404_NOT_FOUND,
            response_example=DocResponseExample(
                description="Запрос участников не существующего чата",
                example=_chat_not_exist_example
            )
        )
    ]
).to_openapi()


add_chat_member_responses = DocResponses.get_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_201_CREATED,
            response_example=DocResponseExample(
                description="Успешное добавление участника к чату",
                example=_success_add_chat_member_example
            )
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_403_FORBIDDEN,
            response_example=DocResponseExample(
                description="Добавление в чат от не участника чата",
                example=_user_not_chat_member_example
            )
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_404_NOT_FOUND,
            response_example=DocResponseExample(
                description="Попытка добавить не существующего пользователя в чат",
                example=_not_exist_user_example
            )
        )
    ]
).to_openapi()

delete_chat_member_responses = DocResponses.get_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешное удаление участника из чата",
                example=_success_delete_chat_member_example
            )
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_403_FORBIDDEN,
            response_example=DocResponseExample(
                description="Только создатель может удалять из чата",
                example=_user_is_not_chat_creator_example
            )
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_404_NOT_FOUND,
            response_example=DocResponseExample(
                description="Не возможно удалить не участника чата",
                example=_login_is_not_chat_member_example
            )
        )
    ]
).to_openapi()
