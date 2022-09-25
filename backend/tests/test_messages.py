from fastapi.testclient import TestClient

from backend.services.ws import MessageType
from backend.tests.base import BaseTest
from backend.tests.conftest import TEST_CHAT_ID, messages, SECOND_CHAT_ID, SECOND_CHAT_NAME, TEST_CHAT_NAME


class TestMessages(BaseTest):
    messages_url = "/api/messages/"

    def test_success_change_message_text(self, client: TestClient):
        change_message_id = "1"
        new_message_text = "Новый текст"

        with client.websocket_connect("ws/user") as user_ws, \
                client.websocket_connect("ws/user1") as user1_ws, \
                client.websocket_connect("ws/new") as new_ws:
            # Необходимо указывать пользователей в порядке подключения
            ws_users = ["user", "user1", "new"]
            # Что бы прочитать статусные сообщения
            for index, ws in enumerate((user_ws, user1_ws, new_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])

            response = client.put(
                url=f"{self.messages_url}{change_message_id}",
                headers=self.get_authorization_headers(),
                json={"text": new_message_text}
            )
            assert response.status_code == 200
            assert response.json() == {"message": "Текст сообщения изменён"}
            self._check_ws_change_message_text_notification(
                ws_list=[user_ws, user1_ws, new_ws],
                message_id=change_message_id,
                new_text=new_message_text,
                chat_id=TEST_CHAT_ID
            )

    @staticmethod
    def _check_ws_change_message_text_notification(ws_list, message_id: str, new_text: str, chat_id: str) -> None:
        for ws in ws_list:
            ws_message = ws.receive_json()
            assert ws_message["type"] == MessageType.CHANGE_MESSAGE_TEXT
            assert ws_message["data"]["chat_id"] == chat_id
            assert ws_message["data"]["message_id"] == message_id
            assert ws_message["data"]["text"] == new_text
            assert ws_message["data"]["change_time"] is not None

    def test_change_message_text_not_auth(self, client: TestClient):
        change_message_id = "1"
        new_message_text = "Новый текст"
        response = client.put(
            url=f"{self.messages_url}{change_message_id}",
            json={"text": new_message_text}
        )
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_change_message_text_empty_text(self, client: TestClient):
        change_message_id = "1"
        new_message_text = ""

        response = client.put(
            url=f"{self.messages_url}{change_message_id}",
            headers=self.get_authorization_headers(),
            json={"text": new_message_text}
        )
        assert response.status_code == 400
        assert response.json() == self.exception_response("Сообщение не может быть пустым")

    def test_change_message_text_bad_message_id(self, client: TestClient):
        bad_message_id = "bad_id"
        new_message_text = "Привет"

        response = client.put(
            url=f"{self.messages_url}{bad_message_id}",
            headers=self.get_authorization_headers(),
            json={"text": new_message_text}
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response(f"Сообщение с id {bad_message_id} не найдено")

    def test_change_message_text_not_owner(self, client: TestClient):
        tokens = self.login(client=client, username="user1", password="password1")
        change_message_id = "1"
        new_message_text = "Новый текст"

        response = client.put(
            url=f"{self.messages_url}{change_message_id}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"text": new_message_text}
        )
        assert response.status_code == 403
        assert response.json() == self.exception_response("Только автор может менять сообщение!")

    def test_change_message_text_same_text(self, client: TestClient):
        change_message_id = messages[0].id
        same_message_text = messages[0].text

        response = client.put(
            url=f"{self.messages_url}{change_message_id}",
            headers=self.get_authorization_headers(),
            json={"text": same_message_text}
        )
        assert response.status_code == 400
        assert response.json() == self.exception_response("У сообщения уже такой текст")

    def test_success_delete_message(self, client: TestClient):
        delete_message_id = "1"

        with client.websocket_connect("ws/user") as user_ws, \
                client.websocket_connect("ws/user1") as user1_ws, \
                client.websocket_connect("ws/new") as new_ws:
            # Необходимо указывать пользователей в порядке подключения
            ws_users = ["user", "user1", "new"]
            # Что бы прочитать статусные сообщения
            for index, ws in enumerate((user_ws, user1_ws, new_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])

            response = client.delete(
                url=f"{self.messages_url}{delete_message_id}",
                headers=self.get_authorization_headers()
            )
            assert response.status_code == 200
            assert response.json() == {"message": "Сообщение удалено"}
            self._check_ws_delete_message_notification(
                ws_list=[user_ws, user1_ws, new_ws],
                message_id=delete_message_id,
                chat_id=TEST_CHAT_ID
            )

    @staticmethod
    def _check_ws_delete_message_notification(ws_list, message_id: str, chat_id: str):
        for ws in ws_list:
            ws_message = ws.receive_json()
            assert ws_message["type"] == MessageType.DELETE_MESSAGE
            assert ws_message["data"]["chat_id"] == chat_id
            assert ws_message["data"]["message_id"] == message_id

    def test_delete_message_not_auth(self, client: TestClient):
        delete_message_id = "1"
        response = client.delete(
            url=f"{self.messages_url}{delete_message_id}",
        )
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_delete_message_bad_message_id(self, client: TestClient):
        bad_message_id = "bad_id"
        response = client.delete(
            url=f"{self.messages_url}{bad_message_id}",
            headers=self.get_authorization_headers()
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response(f"Сообщение с id {bad_message_id} не найдено")

    def test_delete_message_not_owner(self, client: TestClient):
        tokens = self.login(client=client, username="user1", password="password1")
        delete_message_id = "1"

        response = client.delete(
            url=f"{self.messages_url}{delete_message_id}",
            headers=self.get_authorization_headers(access_token=tokens.access_token)
        )
        assert response.status_code == 403
        assert response.json() == self.exception_response("Только автор может удалять сообщение!")

    def test_success_get_all_messages(self, client: TestClient):
        response = client.get(
            url=self.messages_url,
            headers=self.get_authorization_headers()
        )
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert TEST_CHAT_ID in response.json().keys()
        assert SECOND_CHAT_ID in response.json().keys()
        assert response.json()[TEST_CHAT_ID]["chat_name"] == TEST_CHAT_NAME
        assert response.json()[SECOND_CHAT_ID]["chat_name"] == SECOND_CHAT_NAME
        assert response.json()[TEST_CHAT_ID]["creator"] == "user"
        assert response.json()[SECOND_CHAT_ID]["creator"] == "user"
        assert len(response.json()[TEST_CHAT_ID]["messages"]) == 3
        assert len(response.json()[SECOND_CHAT_ID]["messages"]) == 0

        self._check_user_test_chat_messages(
            test_chat_messages=response.json()[TEST_CHAT_ID]["messages"]
        )

    @staticmethod
    def _check_user_test_chat_messages(test_chat_messages: list[dict]):
        assert isinstance(test_chat_messages, list)
        for index, test_message in enumerate(messages):
            message = test_chat_messages[index]
            assert isinstance(message, dict)
            assert message["login"] == "user"
            assert message["text"] == test_message.text
            assert message["type"] == MessageType.TEXT
            assert message["time"] is not None
            assert message["change_time"] is None

    def test_get_all_messages_not_auth(self, client: TestClient):
        response = client.get(url=self.messages_url)
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_success_get_chat_messages(self, client: TestClient):
        response = client.get(
            url=f"{self.messages_url}{TEST_CHAT_ID}",
            headers=self.get_authorization_headers()
        )
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert response.json()["chat_name"] == TEST_CHAT_NAME
        assert response.json()["creator"] == "user"
        assert len(response.json()["messages"]) == 3
        self._check_user_test_chat_messages(
            test_chat_messages=response.json()["messages"]
        )

    def test_get_chat_messages_not_auth(self, client: TestClient):
        response = client.get(url=f"{self.messages_url}{TEST_CHAT_ID}")
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_get_chat_messages_not_exist_chat_id(self, client: TestClient):
        not_exist_chat_id = "not_exist_chat_id"
        response = client.get(
            url=f"{self.messages_url}{not_exist_chat_id}",
            headers=self.get_authorization_headers()
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response(f"Чата с id {not_exist_chat_id} не существует")
