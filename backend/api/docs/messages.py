from fastapi import status

from backend.core.docs import DocResponses, DocResponseExample, StatusCodeDocResponseExample
from backend.models import ChatMessages, MessageData

_success_get_all_messages_example = {
    "MAIN": ChatMessages(
        chat_name="Главная",
        creator="admin",
        messages=[
            MessageData(login="admin", text="Привет участникам чата", time="24.08.22 17:50", message_id="1", type="TEXT", is_read=True, change_time=""), # noqa
            MessageData(login="test", text="Привет", time="24.08.22 17:52", message_id="2", type="TEXT", is_read=True, change_time=""), # noqa
            MessageData(login="test", text="test добавил пользователя test4", time="24.08.22 17:54", message_id="30154158-f159-4db6-a9ac-2b1a2ec2c050", type="INFO", is_read=True, change_time=""), # noqa
        ]
    ).dict(),
    "c724bf8d-9da5-41fe-aebe-8bbd0c861881": ChatMessages(
        chat_name="от Test'a",
        creator="test",
        messages=[
            MessageData(login="test", text="rer", time="22.06.22 20:35", message_id="a7171e1e-6209-4248-8045-17d25a9dd619", type="TEXT", is_read=True, change_time=""), # noqa
            MessageData(login="new", text="мм?", time="22.06.22 20:37", message_id="13f34e1c-eb81-473f-af1f-5d4cf8eaa0f9", type="TEXT", is_read=True, change_time=""), # noqa
            MessageData(login="admin", text="хватит баловаться)", time="27.06.22 20:11", message_id="96f2e552-dddc-4a7e-af7a-1723f2c0cea3", type="TEXT", is_read=False, change_time="27.06.22 20:11"), # noqa
        ]
    ).dict()
}


get_all_messages_responses = DocResponses.create_instance_with_not_auth_response(
    responses=[
        StatusCodeDocResponseExample(
            status_code=status.HTTP_200_OK,
            response_example=DocResponseExample(
                description="Успешное получение сообщений",
                example=_success_get_all_messages_example
            )
        )
    ]
).to_openapi()
