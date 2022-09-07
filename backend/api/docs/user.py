from fastapi import status

from backend.core.docs import DocResponses, DocResponseExample, StatusCodeDocResponseExample
from backend.models import User

_success_change_user_data_example = User(
    id=1,
    login="user",
    name="Новое имя",
    surname="Новая фамилия"
).dict()

_success_get_user_info_example = User(
    id=1,
    login="user",
    name="Имя пользователя",
    surname="Фамилия пользователя"
).dict()

change_user_data_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешное изменение данных пользователя",
                example=_success_change_user_data_example
            )
        )
    ]
).to_openapi()

upload_avatar_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_201_CREATED,
            response_example=DocResponseExample(
                description="Успешная загрузка аватара",
                example={"avatar_file": "1d404bfb-f42b-497b-8318-133a444a5966.jpeg"}
            )
        )
    ]
).to_openapi()

get_login_avatar_file_responses = {
    200: {
        "content-type": "image/png",
        "content": {"image/png": {}},
        "description": "Файл аватара пользователя",
    }
}

get_login_avatar_filename_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешное получение названия файла аватара пользователя",
                example={"avatar_file": "1d404bfb-f42b-497b-8318-133a444a5966.jpeg"}
            )
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_404_NOT_FOUND,
            response_example=DocResponseExample(
                description="Пользователя не существует",
                example={"detail": "Профиль пользователя с логином 'login' не найден"}
            )
        )
    ]
).to_openapi()

get_user_info_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешное получение информации о пользователе",
                example=_success_get_user_info_example
            )
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_404_NOT_FOUND,
            response_example=DocResponseExample(
                description="Запрашиваемый пользователь не существует",
                example={"detail": "Пользователь с логином 'login' не найден"}
            )
        )
    ]
).to_openapi()
