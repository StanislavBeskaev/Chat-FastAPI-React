from fastapi.testclient import TestClient

from backend.services.ws import MessageType
from backend.tests.base import BaseTest
from backend.tests.conftest import TEST_CHAT_ID, TEST_CHAT_NAME, users


class TestChats(BaseTest):
    chats_url = "/api/chats/"

    def test_success_create_new_chat(self, client: TestClient):
        new_chat_name = "Новый чат"

        with client.websocket_connect("ws/user") as user_ws, \
                client.websocket_connect("ws/user1") as user1_ws, \
                client.websocket_connect("ws/new") as new_ws:
            response = client.post(
                url=self.chats_url,
                headers=self.get_authorization_headers(),
                json={"chat_name": new_chat_name, "members": ["user1", "user", "new"]}
            )
            assert response.status_code == 201
            assert response.json() == {"message": f"Чат {new_chat_name} успешно создан"}

            # Необходимо указывать пользователей в порядке подключения
            ws_users = ["user", "user1", "new"]
            for index, ws in enumerate((user_ws, user1_ws, new_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])
                ws_message = ws.receive_json()
                assert ws_message["type"] == MessageType.NEW_CHAT
                assert ws_message["data"]["creator"] == self.DEFAULT_USER
                assert ws_message["data"]["chat_name"] == new_chat_name

    def test_create_new_chat_not_auth(self, client: TestClient):
        response = client.post(
            self.chats_url
        )
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_create_new_chat_empty_chat_name(self, client: TestClient):
        response = client.post(
            url=self.chats_url,
            headers=self.get_authorization_headers(),
            json={"chat_name": "", "members": ["user1", "user", "new"]}
        )
        assert response.status_code == 400
        assert response.json() == self.exception_response("Не указано имя чата")

    def test_create_new_chat_blank_chat_members(self, client: TestClient):
        response = client.post(
            url=self.chats_url,
            headers=self.get_authorization_headers(),
            json={"chat_name": "Новый чат", "members": []}
        )
        assert response.status_code == 400
        assert response.json() == self.exception_response("Не указаны участники чата")

    def test_create_new_chat_few_chat_members(self, client: TestClient):
        response = client.post(
            url=self.chats_url,
            headers=self.get_authorization_headers(),
            json={"chat_name": "Новый чат", "members": ["user"]}
        )
        assert response.status_code == 400
        assert response.json() == self.exception_response("Необходимо добавить хотя бы ещё одного участника")

    def test_create_new_chat_not_exist_user(self, client: TestClient):
        response = client.post(
            url=self.chats_url,
            headers=self.get_authorization_headers(),
            json={"chat_name": "Новый чат", "members": ["user", "bad_User"]}
        )
        assert response.status_code == 400
        assert response.json() == self.exception_response("В списке участников есть не существующие пользователи")

    def test_success_change_chat_name(self, client: TestClient):
        new_name = "тестовый"

        with client.websocket_connect("ws/user") as user_ws, \
                client.websocket_connect("ws/user1") as user1_ws, \
                client.websocket_connect("ws/new") as new_ws:
            response = client.put(
                url=f"{self.chats_url}{TEST_CHAT_ID}",
                headers=self.get_authorization_headers(),
                json={"chat_name": new_name}
            )
            assert response.status_code == 200
            assert response.json() == {"message": "Название чата успешно изменено"}

            ws_users = ["user", "user1", "new"]
            for index, ws in enumerate((user_ws, user1_ws, new_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])
                ws_message = ws.receive_json()
                assert ws_message["type"] == MessageType.CHANGE_CHAT_NAME
                assert ws_message["data"]["chat_name"] == new_name
                assert ws_message["data"]["chat_id"] == TEST_CHAT_ID

    def test_change_chat_name_not_auth(self, client: TestClient):
        response = client.put(
            url=f"{self.chats_url}{TEST_CHAT_ID}",
            json={"chat_name": "новое название"}
        )
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_change_chat_name_empty_name(self, client: TestClient):
        response = client.put(
            url=f"{self.chats_url}{TEST_CHAT_ID}",
            headers=self.get_authorization_headers(),
            json={"chat_name": ""}
        )
        assert response.status_code == 400
        assert response.json() == self.exception_response("Укажите название чата")

    def test_change_chat_name_same_name(self, client: TestClient):
        response = client.put(
            url=f"{self.chats_url}{TEST_CHAT_ID}",
            headers=self.get_authorization_headers(),
            json={"chat_name": TEST_CHAT_NAME}
        )
        assert response.status_code == 400
        assert response.json() == self.exception_response("Название чата совпадает с текущим")

    def test_change_chat_name_not_exist_chat(self, client: TestClient):
        bad_chat_id = "bad_chat_id"
        response = client.put(
            url=f"{self.chats_url}{bad_chat_id}",
            headers=self.get_authorization_headers(),
            json={"chat_name": TEST_CHAT_NAME}
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response(f"Чата с id {bad_chat_id} не существует")

    def test_change_chat_name_not_creator(self, client: TestClient):
        not_creator = users[1]
        tokens = self.login(client=client, username=not_creator.login, password="password1")
        response = client.put(
            url=f"{self.chats_url}{TEST_CHAT_ID}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"chat_name": TEST_CHAT_NAME}
        )

        assert response.status_code == 403
        assert response.json() == self.exception_response("Изменить название чата может только создатель")
