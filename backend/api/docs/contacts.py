from fastapi import status

from backend.core.docs import DocResponses, DocResponseExample, StatusCodeDocResponseExample
from backend.models import Contact

_success_get_contacts_example = [
    {"login": "admin", "name": "Админ", "surname": "Главный"},
    {"login": "user", "name": "Пользователь", "surname": ""},
    {"login": "test", "name": "Тест", "surname": "Фамилия"},
]

_success_create_contact_example = Contact(login="contact_login", name="user name", surname="user surname").dict()

_not_found_delete_contact_request_example = {
    "detail": "Пользователь с логином 'login' не найден/ Контакт с логином 'login' не найден"
}

_user_contact_not_found_status_code_example = StatusCodeDocResponseExample(
    status_code=status.HTTP_404_NOT_FOUND,
    response_example=DocResponseExample(
        description="Пользователь/контакт не найден", example=_not_found_delete_contact_request_example
    ),
)

_success_get_contact_info_example = Contact(
    login="contact login", name="contact name", surname="contact surname"
).dict()

get_contacts_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешное получение контактов", example=_success_get_contacts_example
            ),
        )
    ]
).to_openapi()

create_contact_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_201_CREATED,
            response_example=DocResponseExample(
                description="Успешное создание контакта", example=_success_create_contact_example
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_400_BAD_REQUEST,
            response_example=DocResponseExample(
                description="Нельзя добавить себя в контакты", example={"detail": "Нельзя добавить себя в контакты"}
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_404_NOT_FOUND,
            response_example=DocResponseExample(
                description="Запрос на добавление в контакты не существующего пользователя",
                example={"detail": "Пользователь с логином 'login' не найден"},
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_409_CONFLICT,
            response_example=DocResponseExample(
                description="Пользователь уже есть в контактах", example={"detail": "Такой контакт уже существует"}
            ),
        ),
    ]
).to_openapi()

delete_contact_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешное удаление контакта", example={"message": f"Контакт login удалён"}
            ),
        ),
        _user_contact_not_found_status_code_example,
    ]
).to_openapi()


get_contact_info_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешное получение данных контакта", example=_success_get_contact_info_example
            ),
        ),
        _user_contact_not_found_status_code_example,
    ]
).to_openapi()

change_contact_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешное изменение контакта", example={"message": f"Контакт login изменён"}
            ),
        ),
        _user_contact_not_found_status_code_example,
    ]
).to_openapi()
