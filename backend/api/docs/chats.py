from fastapi import status

from backend.core.docs import DocResponseExample, DocResponses, StatusCodeDocResponseExample

_success_create_new_chat_example = {"message": "Чат new_chat успешно создан"}
_bad_request_create_new_chat_example = {
    "detail": "Не указано имя чата/ Не указаны участники чата/ Необходимо добавить хотя бы ещё одного участника/ В списке участников есть не существующие пользователи"  # noqa
}

_success_change_chat_name_example = {"message": "Название чата успешно изменено"}
_bad_request_change_chat_name_example = {"detail": "Укажите название чата/ Название чата совпадает с текущим"}
_not_creator_error_change_chat_name_example = {"detail": "Изменить название чата может только создатель"}

_chat_not_found_example = {"detail": "Чата с id chat_id не существует"}

create_new_chat_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_201_CREATED,
            response_example=DocResponseExample(
                description="Успешное создание чата", example=_success_create_new_chat_example
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_400_BAD_REQUEST,
            response_example=DocResponseExample(
                description="Не корректный запрос на создание чата", example=_bad_request_create_new_chat_example
            ),
        ),
    ]
).to_openapi()

change_chat_name_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешное изменение названия чата", example=_success_change_chat_name_example
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_400_BAD_REQUEST,
            response_example=DocResponseExample(
                description="Не корректный запрос на изменение названия чата",
                example=_bad_request_change_chat_name_example,
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_403_FORBIDDEN,
            response_example=DocResponseExample(
                description="Только создатель может изменить название чата",
                example=_not_creator_error_change_chat_name_example,
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_404_NOT_FOUND,
            response_example=DocResponseExample(description="Чат не найден", example=_chat_not_found_example),
        ),
    ]
).to_openapi()


try_leave_chat_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Получено предупредительное сообщение выхода из чата",
                example={
                    "message": "Вы уверены, что хотите покинуть чат?/"
                    "Вы создатель чата. Это приведёт к удалению чата. Вы уверены?"
                },
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_400_BAD_REQUEST,
            response_example=DocResponseExample(
                description="Вы не участник чата", example={"detail": "Вы не участник чата"}
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_403_FORBIDDEN,
            response_example=DocResponseExample(
                description="Нельзя покинуть главный чат", example={"detail": "Нельзя покинуть главный чат"}
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_404_NOT_FOUND,
            response_example=DocResponseExample(description="Чат не найден", example=_chat_not_found_example),
        ),
    ]
).to_openapi()


leave_chat_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Выход из чата выполнен", example={"message": "Вы вышли из чата"}
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_400_BAD_REQUEST,
            response_example=DocResponseExample(
                description="Вы не участник чата", example={"detail": "Вы не участник чата"}
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_403_FORBIDDEN,
            response_example=DocResponseExample(
                description="Нельзя покинуть главный чат", example={"detail": "Нельзя покинуть главный чат"}
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_404_NOT_FOUND,
            response_example=DocResponseExample(description="Чат не найден", example=_chat_not_found_example),
        ),
    ]
).to_openapi()
