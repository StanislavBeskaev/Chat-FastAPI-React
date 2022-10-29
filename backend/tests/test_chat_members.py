from fastapi.testclient import TestClient

from backend import tables
from backend.services.ws.constants import MessageType
from backend.tests import data as test_data
from backend.tests.base import BaseTest


class TestChatMembers(BaseTest):
    chat_members_url = "/api/chat_members/"

    def test_success_add_chat_member(self, client: TestClient):
        with client.websocket_connect("ws/user") as user_ws, client.websocket_connect(
            "ws/user1"
        ) as user1_ws, client.websocket_connect("ws/new") as new_ws:
            # Необходимо указывать пользователей в порядке подключения
            ws_users = ["user", "user1", "new"]
            # Что бы прочитать статусные сообщения
            for index, ws in enumerate((user_ws, user1_ws, new_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])
            response = client.post(
                url=f"{self.chat_members_url}{test_data.TEST_CHAT_ID}",
                headers=self.get_authorization_headers(),
                json={"login": "user2"},
            )
            assert response.status_code == 201
            assert response.json() == {"message": f"Пользователь user2 добавлен к чату: {test_data.TEST_CHAT_ID}"}

            self._check_ws_add_to_chat_notifications(
                ws_list=[user_ws, user1_ws, new_ws],
                chat_id=test_data.TEST_CHAT_ID,
                action_user="user",
                user="user2",
                chat_name=test_data.TEST_CHAT_NAME,
            )

    @staticmethod
    def _check_ws_add_to_chat_notifications(ws_list, chat_id: str, action_user: str, user: str, chat_name: str):
        for ws in ws_list:
            info_message = ws.receive_json()
            assert info_message["type"] == MessageType.TEXT
            assert info_message["data"]["login"] == action_user
            assert info_message["data"]["text"] == f"{action_user} добавил пользователя {user}"
            assert info_message["data"]["time"] is not None
            assert info_message["data"]["chat_id"] == chat_id
            assert info_message["data"]["message_id"] is not None
            assert info_message["data"]["type"] == tables.MessageType.INFO

            add_to_chat_message = ws.receive_json()
            assert add_to_chat_message["type"] == MessageType.ADD_TO_CHAT
            assert add_to_chat_message["data"]["login"] == user
            assert add_to_chat_message["data"]["chat_id"] == chat_id
            assert add_to_chat_message["data"]["chat_name"] == chat_name

    def test_add_chat_member_not_auth(self, client: TestClient):
        response = client.post(url=f"{self.chat_members_url}{test_data.TEST_CHAT_ID}", json={"login": "user1"})
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_add_chat_member_user_already_in_chat(self, client: TestClient):
        candidate = "new"
        response = client.post(
            url=f"{self.chat_members_url}{test_data.TEST_CHAT_ID}",
            headers=self.get_authorization_headers(),
            json={"login": candidate},
        )
        assert response.status_code == 409
        assert response.json() == self.exception_response(
            f"В чате {test_data.TEST_CHAT_ID} уже есть пользователь {candidate}"
        )

    def test_add_chat_members_not_exist_chat(self, client: TestClient):
        candidate = "new"
        not_exist_chat_id = "bad_chat_id"
        response = client.post(
            url=f"{self.chat_members_url}{not_exist_chat_id}",
            headers=self.get_authorization_headers(),
            json={"login": candidate},
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response(f"Чата с id {not_exist_chat_id} не существует")

    def test_add_chat_member_by_not_chat_member(self, client: TestClient):
        candidate = "new"
        response = client.post(
            url=f"{self.chat_members_url}{test_data.TEST_CHAT_ID}",
            headers=self.get_authorization_headers(username="user2", password="user2"),
            json={"login": candidate},
        )
        assert response.status_code == 403
        assert response.json() == self.exception_response(f"Вы не участник чата {test_data.TEST_CHAT_ID}")

    def test_add_chat_members_not_exist_login(self, client: TestClient):
        not_exist_login = "bad_login"
        response = client.post(
            url=f"{self.chat_members_url}{test_data.TEST_CHAT_ID}",
            headers=self.get_authorization_headers(),
            json={"login": not_exist_login},
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response(f"Пользователя с логином {not_exist_login} не существует")

    def test_success_delete_chat_member(self, client: TestClient):
        removable_user = "new"

        with client.websocket_connect("ws/user") as user_ws, client.websocket_connect("ws/new") as new_ws:
            # Необходимо указывать пользователей в порядке подключения
            ws_users = ["user", "new"]
            # Что бы прочитать статусные сообщения
            for index, ws in enumerate((user_ws, new_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])

            response = client.delete(
                url=f"{self.chat_members_url}{test_data.TEST_CHAT_ID}",
                headers=self.get_authorization_headers(),
                json={"login": removable_user},
            )
            assert response.status_code == 200
            assert response.json() == {
                "message": f"Пользователь {removable_user} удалён из чата: {test_data.TEST_CHAT_ID}"
            }

            self._check_ws_delete_from_chat_message(
                ws_list=[user_ws, new_ws],
                chat_id=test_data.TEST_CHAT_ID,
                removable_user=removable_user,
                chat_name=test_data.TEST_CHAT_NAME,
            )
            self._check_ws_delete_from_chat_info_message(
                ws_list=[user_ws],
                chat_id=test_data.TEST_CHAT_ID,
                action_user=self.DEFAULT_USER,
                removable_user=removable_user,
            )

    @staticmethod
    def _check_ws_delete_from_chat_message(ws_list, chat_id: str, removable_user: str, chat_name: str):
        for ws in ws_list:
            delete_from_chat_message = ws.receive_json()
            assert delete_from_chat_message["type"] == MessageType.DELETE_FROM_CHAT
            assert delete_from_chat_message["data"]["login"] == removable_user
            assert delete_from_chat_message["data"]["chat_id"] == chat_id
            assert delete_from_chat_message["data"]["chat_name"] == chat_name

    @staticmethod
    def _check_ws_delete_from_chat_info_message(ws_list, chat_id: str, action_user: str, removable_user: str):
        for ws in ws_list:
            info_message = ws.receive_json()
            assert info_message["type"] == MessageType.TEXT
            assert info_message["data"]["login"] == action_user
            assert info_message["data"]["text"] == f"{action_user} удалил пользователя {removable_user}"
            assert info_message["data"]["time"] is not None
            assert info_message["data"]["chat_id"] == chat_id
            assert info_message["data"]["message_id"] is not None
            assert info_message["data"]["type"] == tables.MessageType.INFO

    def test_delete_chat_member_not_auth(self, client: TestClient):
        removable_user = "new"
        response = client.delete(url=f"{self.chat_members_url}{test_data.TEST_CHAT_ID}", json={"login": removable_user})
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_delete_chat_member_user_not_in_chat(self, client: TestClient):
        user_not_in_test_chat = "some"
        response = client.delete(
            url=f"{self.chat_members_url}{test_data.TEST_CHAT_ID}",
            headers=self.get_authorization_headers(),
            json={"login": user_not_in_test_chat},
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response(f"Пользователя {user_not_in_test_chat} нет в чате")

    def test_delete_chat_member_not_exist_chat(self, client: TestClient):
        removable_user = "new"
        not_exist_chat_id = "not_exist_chat_id"
        response = client.delete(
            url=f"{self.chat_members_url}{not_exist_chat_id}",
            headers=self.get_authorization_headers(),
            json={"login": removable_user},
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response(f"Чата с id {not_exist_chat_id} не существует")

    def test_delete_chat_member_not_exist_login(self, client: TestClient):
        not_exist_user = "bad_login"
        response = client.delete(
            url=f"{self.chat_members_url}{test_data.TEST_CHAT_ID}",
            headers=self.get_authorization_headers(),
            json={"login": not_exist_user},
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response(f"Пользователя с логином {not_exist_user} не существует")

    def test_delete_chat_member_by_not_chat_creator(self, client):
        response = client.delete(
            url=f"{self.chat_members_url}{test_data.TEST_CHAT_ID}",
            headers=self.get_authorization_headers(username="new", password="new"),
            json={"login": "new"},
        )
        assert response.status_code == 403
        assert response.json() == self.exception_response("Только создатель может удалять из чата")

    def test_success_get_chat_members(self, client: TestClient):
        test_chat_members = ("user", "user1", "new")
        response = client.get(
            url=f"{self.chat_members_url}{test_data.TEST_CHAT_ID}", headers=self.get_authorization_headers()
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        for chat_member in response.json():
            assert chat_member["login"] in test_chat_members
            assert chat_member["is_online"] is False

        with client.websocket_connect("ws/user"):
            response = client.get(
                url=f"{self.chat_members_url}{test_data.TEST_CHAT_ID}", headers=self.get_authorization_headers()
            )
            assert response.status_code == 200
            assert isinstance(response.json(), list)
            for chat_member in response.json():
                assert chat_member["login"] in test_chat_members
                if chat_member["login"] == "user":
                    assert chat_member["is_online"] is True
                else:
                    assert chat_member["is_online"] is False

    def test_get_chat_members_not_auth(self, client: TestClient):
        response = client.get(url=f"{self.chat_members_url}{test_data.TEST_CHAT_ID}")
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_get_chat_members_not_exist_chat(self, client: TestClient):
        not_exist_chat_chat_id = "not_exist_chat_chat_id"
        response = client.get(
            url=f"{self.chat_members_url}{not_exist_chat_chat_id}", headers=self.get_authorization_headers()
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response(f"Чата с id {not_exist_chat_chat_id} не существует")

    def test_get_chat_members_by_not_chat_member(self, client: TestClient):
        response = client.get(
            url=f"{self.chat_members_url}{test_data.TEST_CHAT_ID}",
            headers=self.get_authorization_headers(username="user2", password="user2"),
        )
        assert response.status_code == 403
        assert response.json() == self.exception_response(f"Вы не участник чата {test_data.TEST_CHAT_ID}")
