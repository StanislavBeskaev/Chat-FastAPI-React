from fastapi import status

from backend.core.docs import DocResponseExample, StatusCodeDocResponseExample, DocResponses
from backend.models import Tokens, User


_user_already_exist_registration_example = {"detail": "Пользователь с таким логином уже существует"}
_success_registration_example = Tokens(
    access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NjIxOTY5NjEsIm5iZiI6MTY2MjE5Njk2MSwiZXhwIjoxNjYyMTk3ODYxLCJraW5kIjoiYWNjZXNzIiwidXNlciI6eyJuYW1lIjoiIiwic3VybmFtZSI6IiIsImxvZ2luIjoidXNlciIsImlkIjoxOX19.r1u2kvadf4IHk84IsYpd2CdCS9NS4ZQ9vNTIpAg3GZ4", # noqa
    refresh_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NjIxOTY5NjEsIm5iZiI6MTY2MjE5Njk2MSwiZXhwIjoxNjY0Nzg4OTYxLCJraW5kIjoicmVmcmVzaCIsInVzZXIiOnsibmFtZSI6IiIsInN1cm5hbWUiOiIiLCJsb2dpbiI6InVzZXIiLCJpZCI6MTl9fQ.9QJJfBlH2f3Hfu6wRvtwyG705OLDjNSi8zEQTW3sV4Q", # noqa
    user=User(
        name="Имя пользователя",
        surname="Фамилия пользователя",
        login="user",
        id=1
    )
).dict()

_success_login_example = _success_registration_example
_wrong_password_login_example = {"detail": "Неверный пароль"}
_user_not_exist_login_example = {"detail": "Пользователь с таким логином не найден"}

_success_refresh_example = _success_registration_example
_not_success_refresh_example = {"detail": "Не удалось обновить токены"}

_success_logout_example = {"message": "Выход из системы выполнен"}
_bad_logout_example = {"detail": "Не валидный refresh_token"}


registration_responses = DocResponses(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_201_CREATED,
            response_example=DocResponseExample(
                description="Успешная регистрация",
                example=_success_registration_example
            )
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_409_CONFLICT,
            response_example=DocResponseExample(
                description="Пользователь с таким логином уже существует",
                example=_user_already_exist_registration_example
            )
        )
    ]
).to_openapi()

login_responses = DocResponses(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешный вход",
                example=_success_login_example,
            )
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_401_UNAUTHORIZED,
            response_example=DocResponseExample(
                description="Неверный пароль",
                example=_wrong_password_login_example
            )
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_404_NOT_FOUND,
            response_example=DocResponseExample(
                description="Пользователь не найден",
                example=_user_not_exist_login_example
            )
        )
    ]
).to_openapi()

refresh_responses = DocResponses(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешное обновление токенов",
                example=_success_refresh_example
            )
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_401_UNAUTHORIZED,
            response_example=DocResponseExample(
                description="Не удалось обновить токены",
                example=_not_success_refresh_example
            )
        )
    ]
).to_openapi()


logout_responses = DocResponses(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешный выход",
                example=_success_logout_example
            )
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_401_UNAUTHORIZED,
            response_example=DocResponseExample(
                description="Не корректный refresh token",
                example=_bad_logout_example
            )
        )
    ]
).to_openapi()
