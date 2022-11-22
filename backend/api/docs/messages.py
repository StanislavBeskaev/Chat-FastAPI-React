from fastapi import status

from backend.core.docs import DocResponseExample, DocResponses, StatusCodeDocResponseExample
from backend.models import ChatMessages, MessageData

_success_get_all_messages_example = {
    "MAIN": ChatMessages(
        chat_name="Главная",
        creator="admin",
        messages=[
            MessageData(
                login="admin",
                text="Привет участникам чата",
                time="24.08.22 17:50",
                message_id="1",
                type="TEXT",
                is_read=True,
                change_time="",
            ),
            MessageData(
                login="test",
                text="Привет",
                time="24.08.22 17:52",
                message_id="2",
                type="TEXT",
                is_read=True,
                change_time="",
            ),
            MessageData(
                login="test",
                text="test добавил пользователя test4",
                time="24.08.22 17:54",
                message_id="30154158-f159-4db6-a9ac-2b1a2ec2c050",
                type="INFO",
                is_read=True,
                change_time="",
            ),
        ],
    ).dict(),
    "c724bf8d-9da5-41fe-aebe-8bbd0c861881": ChatMessages(
        chat_name="от Test'a",
        creator="test",
        messages=[
            MessageData(
                login="test",
                text="rer",
                time="22.06.22 20:35",
                message_id="a7171e1e-6209-4248-8045-17d25a9dd619",
                type="TEXT",
                is_read=True,
                change_time="",
            ),
            MessageData(
                login="new",
                text="мм?",
                time="22.06.22 20:37",
                message_id="13f34e1c-eb81-473f-af1f-5d4cf8eaa0f9",
                type="TEXT",
                is_read=True,
                change_time="",
            ),
            MessageData(
                login="admin",
                text="хватит баловаться)",
                time="27.06.22 20:11",
                message_id="96f2e552-dddc-4a7e-af7a-1723f2c0cea3",
                type="TEXT",
                is_read=False,
                change_time="27.06.22 20:11",
            ),
        ],
    ).dict(),
}


get_all_messages_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешное получение сообщений", example=_success_get_all_messages_example
            ),
        )
    ]
).to_openapi()

get_chat_messages_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешное получение сообщений чата", example=_success_get_all_messages_example["MAIN"]
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_404_NOT_FOUND,
            response_example=DocResponseExample(
                "Запрос сообщений не существующего чата",
                example={"detail": "Чата с id not_exist_chat_id не существует"},
            ),
        ),
    ]
).to_openapi()

change_message_text_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешное изменение текста сообщения", example={"message": "Текст сообщения изменён"}
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_400_BAD_REQUEST,
            response_example=DocResponseExample(
                description="Не корректный запрос",
                example={"detail": "Сообщение не может быть пустым/ У сообщения уже такой текст"},
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_403_FORBIDDEN,
            response_example=DocResponseExample(
                description="Только автор может менять текст сообщения",
                example={"detail": "Только автор может менять сообщение!"},
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_404_NOT_FOUND,
            response_example=DocResponseExample(
                description="Попытка изменить не существующее сообщение",
                example={"detail": "Сообщение с id message_id не найдено"},
            ),
        ),
    ]
).to_openapi()

delete_message_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешное удаление сообщения", example={"message": "Сообщение удалено"}
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_403_FORBIDDEN,
            response_example=DocResponseExample(
                description="Только автор может удалять сообщение",
                example={"detail": "Только автор может удалять сообщение!"},
            ),
        ),
        StatusCodeDocResponseExample(
            status_code=status.HTTP_404_NOT_FOUND,
            response_example=DocResponseExample(
                description="Попытка удалить не существующее сообщение",
                example={"detail": "Сообщение с id message_id не найдено"},
            ),
        ),
    ]
).to_openapi()
