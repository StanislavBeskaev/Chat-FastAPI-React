import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.db.mock.facade import MockDBFacade
from backend.services.ws import MessageType
from backend.settings import Settings
from backend.tests import data as test_data
from backend.tests.base import BaseTest


class TestChats(BaseTest):
    chats_url = "/api/chats/"

    def test_success_create_new_chat(self, client: TestClient):
        new_chat_name = "Новый чат"

        with client.websocket_connect("ws/user") as user_ws, client.websocket_connect(
            "ws/user1"
        ) as user1_ws, client.websocket_connect("ws/new") as new_ws:
            response = client.post(
                url=self.chats_url,
                headers=self.get_authorization_headers(),
                json={"chat_name": new_chat_name, "members": ["user1", "user", "new"]},
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
        response = client.post(self.chats_url)
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_create_new_chat_empty_chat_name(self, client: TestClient):
        response = client.post(
            url=self.chats_url,
            headers=self.get_authorization_headers(),
            json={"chat_name": "", "members": ["user1", "user", "new"]},
        )
        assert response.status_code == 400
        assert response.json() == self.exception_response("Не указано имя чата")

    def test_create_new_chat_blank_chat_members(self, client: TestClient):
        response = client.post(
            url=self.chats_url, headers=self.get_authorization_headers(), json={"chat_name": "Новый чат", "members": []}
        )
        assert response.status_code == 400
        assert response.json() == self.exception_response("Не указаны участники чата")

    def test_create_new_chat_few_chat_members(self, client: TestClient):
        response = client.post(
            url=self.chats_url,
            headers=self.get_authorization_headers(),
            json={"chat_name": "Новый чат", "members": ["user"]},
        )
        assert response.status_code == 400
        assert response.json() == self.exception_response("Необходимо добавить хотя бы ещё одного участника")

    def test_create_new_chat_not_exist_user(self, client: TestClient):
        response = client.post(
            url=self.chats_url,
            headers=self.get_authorization_headers(),
            json={"chat_name": "Новый чат", "members": ["user", "bad_User"]},
        )
        assert response.status_code == 400
        assert response.json() == self.exception_response("В списке участников есть не существующие пользователи")

    def test_success_change_chat_name(self, client: TestClient):
        new_name = "тестовый"

        with client.websocket_connect("ws/user") as user_ws, client.websocket_connect(
            "ws/user1"
        ) as user1_ws, client.websocket_connect("ws/new") as new_ws:
            response = client.put(
                url=f"{self.chats_url}{test_data.TEST_CHAT_ID}",
                headers=self.get_authorization_headers(),
                json={"chat_name": new_name},
            )
            assert response.status_code == 200
            assert response.json() == {"message": "Название чата успешно изменено"}

            ws_users = ["user", "user1", "new"]
            for index, ws in enumerate((user_ws, user1_ws, new_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])
                ws_message = ws.receive_json()
                assert ws_message["type"] == MessageType.CHANGE_CHAT_NAME
                assert ws_message["data"]["chat_name"] == new_name
                assert ws_message["data"]["chat_id"] == test_data.TEST_CHAT_ID

    def test_change_chat_name_not_auth(self, client: TestClient):
        response = client.put(url=f"{self.chats_url}{test_data.TEST_CHAT_ID}", json={"chat_name": "новое название"})
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_change_chat_name_empty_name(self, client: TestClient):
        response = client.put(
            url=f"{self.chats_url}{test_data.TEST_CHAT_ID}",
            headers=self.get_authorization_headers(),
            json={"chat_name": ""},
        )
        assert response.status_code == 400
        assert response.json() == self.exception_response("Укажите название чата")

    def test_change_chat_name_same_name(self, client: TestClient):
        response = client.put(
            url=f"{self.chats_url}{test_data.TEST_CHAT_ID}",
            headers=self.get_authorization_headers(),
            json={"chat_name": test_data.TEST_CHAT_NAME},
        )
        assert response.status_code == 400
        assert response.json() == self.exception_response("Название чата совпадает с текущим")

    def test_change_chat_name_not_exist_chat(self, client: TestClient):
        bad_chat_id = "bad_chat_id"
        response = client.put(
            url=f"{self.chats_url}{bad_chat_id}",
            headers=self.get_authorization_headers(),
            json={"chat_name": test_data.TEST_CHAT_NAME},
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response(f"Чата с id {bad_chat_id} не существует")

    def test_change_chat_name_not_creator(self, client: TestClient):
        not_creator = test_data.users[1]
        response = client.put(
            url=f"{self.chats_url}{test_data.TEST_CHAT_ID}",
            headers=self.get_authorization_headers(username=not_creator.login, password=not_creator.password_hash),
            json={"chat_name": test_data.TEST_CHAT_NAME},
        )

        assert response.status_code == 403
        assert response.json() == self.exception_response("Изменить название чата может только создатель")

    def test_success_try_leave_chat_not_creator(self, client: TestClient):
        not_creator = test_data.users[1]
        response = client.get(
            url=f"{self.chats_url}try_leave/{test_data.TEST_CHAT_ID}",
            headers=self.get_authorization_headers(username=not_creator.login, password=not_creator.password_hash),
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Вы уверены, что хотите покинуть чат?"}

    def test_success_try_leave_chat_creator(self, client: TestClient):
        response = client.get(
            url=f"{self.chats_url}try_leave/{test_data.TEST_CHAT_ID}", headers=self.get_authorization_headers()
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Вы создатель чата. Это приведёт к удалению чата. Вы уверены?"}

    def test_try_leave_not_exist_chat(self, client: TestClient):
        bad_chat_id = "bad_chat_id"
        response = client.get(url=f"{self.chats_url}try_leave/{bad_chat_id}", headers=self.get_authorization_headers())
        assert response.status_code == 404
        assert response.json() == self.exception_response(f"Чата с id {bad_chat_id} не существует")

    def test_try_leave_chat_not_auth(self, client: TestClient):
        response = client.get(
            url=f"{self.chats_url}try_leave/{test_data.TEST_CHAT_ID}",
        )

        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_try_leave_chat_not_chat_member(self, client: TestClient):
        response = client.get(
            url=f"{self.chats_url}try_leave/{test_data.TEST_CHAT_ID}",
            headers=self.get_authorization_headers(username="user2", password="user2"),
        )

        assert response.status_code == 400
        assert response.json() == self.exception_response("Вы не участник чата")

    def test_try_leave_main(self, client: TestClient, settings: Settings):
        response = client.get(
            url=f"{self.chats_url}try_leave/{settings.main_chat_id}", headers=self.get_authorization_headers()
        )

        assert response.status_code == 403
        assert response.json() == self.exception_response("Нельзя покинуть главный чат")

    def test_leave_chat_success_not_creator(self, client: TestClient, db_facade: MockDBFacade):
        leaved_chat_id = test_data.TEST_CHAT_ID
        not_creator = test_data.users[1]
        response = client.post(
            url=f"{self.chats_url}leave/{leaved_chat_id}",
            headers=self.get_authorization_headers(username=not_creator.login, password=not_creator.password_hash),
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Вы вышли из чата"}

        test_chat_members = db_facade.get_chat_members(chat_id=leaved_chat_id)
        assert test_chat_members is not None
        assert len(test_chat_members) > 0
        assert not_creator.login not in [member.login for member in test_chat_members]

    def test_leave_chat_success_creator(self, client: TestClient, db_facade: MockDBFacade):
        leaved_chat_id = test_data.TEST_CHAT_ID
        response = client.post(url=f"{self.chats_url}leave/{leaved_chat_id}", headers=self.get_authorization_headers())

        assert response.status_code == 200
        assert response.json() == {"message": "Вы вышли из чата"}

        leaved_chat_messages = db_facade.get_chat_messages(chat_id=leaved_chat_id)
        assert len(leaved_chat_messages) == 0

        leaved_chat_members = db_facade.get_chat_members(chat_id=leaved_chat_id)
        assert len(leaved_chat_members) == 0

        with pytest.raises(HTTPException) as exc_info:
            db_facade.get_chat_by_id(chat_id=leaved_chat_id)
        assert 1 == 1
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == f"Чата с id {leaved_chat_id} не существует"

    def test_leave_chat_not_auth(self, client: TestClient):
        response = client.post(url=f"{self.chats_url}leave/{test_data.TEST_CHAT_ID}")
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_leave_chat_not_exist_chat(self, client: TestClient):
        bad_chat_id = "bad_chat_id"
        response = client.post(url=f"{self.chats_url}leave/{bad_chat_id}", headers=self.get_authorization_headers())
        assert response.status_code == 404
        assert response.json() == self.exception_response(f"Чата с id {bad_chat_id} не существует")

    def test_leave_chat_not_chat_member(self, client: TestClient):
        response = client.post(
            url=f"{self.chats_url}leave/{test_data.TEST_CHAT_ID}",
            headers=self.get_authorization_headers(username="user2", password="user2"),
        )

        assert response.status_code == 400
        assert response.json() == self.exception_response("Вы не участник чата")

    def test_leave_main(self, client: TestClient, settings: Settings):
        response = client.post(
            url=f"{self.chats_url}leave/{settings.main_chat_id}", headers=self.get_authorization_headers()
        )

        assert response.status_code == 403
        assert response.json() == self.exception_response("Нельзя покинуть главный чат")
