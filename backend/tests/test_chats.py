from unittest.mock import patch

from backend import tables
from backend.services.auth import AuthService
from backend.tests.base import BaseTestCase, override_get_session
from backend.services.ws.constants import MessageType


test_users = [
    tables.User(login="user", name="user", surname="", password_hash=AuthService.hash_password("password")),
    tables.User(login="user1", name="user1", surname="", password_hash=AuthService.hash_password("password1")),
    tables.User(login="new", name="new", surname="", password_hash=AuthService.hash_password("password2")),
]
TEST_CHAT_ID = "TEST"
TEST_CHAT_NAME = "Тестовый чат"


class TestChats(BaseTestCase):
    chats_url = "/api/chats/"

    def setUp(self) -> None:
        self.session.bulk_save_objects(test_users)
        users = self.session.query(tables.User).all()

        user = next((user for user in users if user.login == self.DEFAULT_USER))
        test_chat = tables.Chat(id=TEST_CHAT_ID, name=TEST_CHAT_NAME, creator_id=user.id)
        self.session.add(test_chat)

        profiles = []
        test_chat_members = []
        for user in users:
            profiles.append(tables.Profile(user=user.id, avatar_file=None))
            test_chat_members.append(tables.ChatMember(chat_id=test_chat.id, user_id=user.id))
        self.session.bulk_save_objects(profiles)
        self.session.bulk_save_objects(test_chat_members)

        self.session.commit()

        self.get_session_patcher = patch(target="backend.dao.get_session", new=override_get_session)
        self.get_session_patcher.start()

    def tearDown(self) -> None:
        self.session.query(tables.Profile).delete()
        self.session.query(tables.RefreshToken).delete()
        self.session.query(tables.ChatMember).delete()
        self.session.query(tables.Chat).delete()
        self.session.query(tables.User).delete()
        self.session.commit()

        self.get_session_patcher.start()

    def test_success_create_new_chat(self):
        tokens = self.login()
        new_chat_name = "Новый чат"

        with self.client.websocket_connect("ws/user") as user_ws, \
                self.client.websocket_connect("ws/user1") as user1_ws, \
                self.client.websocket_connect("ws/new") as new_ws:
            response = self.client.post(
                url=self.chats_url,
                headers=self.get_authorization_headers(access_token=tokens.access_token),
                json={"chat_name": new_chat_name, "members": ["user1", "user", "new"]}
            )

            self.assertEqual(response.status_code, 200)

            # Необходимо указывать пользователей в порядке подключения
            ws_users = ["user", "user1", "new"]
            for index, ws in enumerate((user_ws, user1_ws, new_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])
                ws_message = ws.receive_json()
                self.assertEqual(ws_message["type"], MessageType.NEW_CHAT)
                self.assertEqual(ws_message["data"]["creator"], self.DEFAULT_USER)
                self.assertEqual(ws_message["data"]["chat_name"], new_chat_name)

    def test_create_new_chat_not_auth(self):
        response = self.client.post(
            self.chats_url
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.NOT_AUTH_RESPONSE)

    def test_create_new_chat_empty_chat_name(self):
        tokens = self.login()
        response = self.client.post(
            url=self.chats_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"chat_name": "", "members": ["user1", "user", "new"]}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Не указано имя чата"})

    def test_create_new_chat_blank_chat_members(self):
        tokens = self.login()
        response = self.client.post(
            url=self.chats_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"chat_name": "Новый чат", "members": []}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Не указаны участники чата"})

    def test_create_new_chat_few_chat_members(self):
        tokens = self.login()
        response = self.client.post(
            url=self.chats_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"chat_name": "Новый чат", "members": ["user"]}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Необходимо добавить хотя бы ещё одного участника"})

    def test_create_new_chat_not_exist_user(self):
        tokens = self.login()
        response = self.client.post(
            url=self.chats_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"chat_name": "Новый чат", "members": ["user", "bad_User"]}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "В списке участников есть не существующие пользователи"})

    def test_success_change_chat_name(self):
        tokens = self.login()
        new_name = "тестовый"

        with self.client.websocket_connect("ws/user") as user_ws, \
                self.client.websocket_connect("ws/user1") as user1_ws, \
                self.client.websocket_connect("ws/new") as new_ws:
            response = self.client.put(
                url=f"{self.chats_url}{TEST_CHAT_ID}",
                headers=self.get_authorization_headers(access_token=tokens.access_token),
                json={"chat_name": new_name}
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Название чата успешно изменено"})

            ws_users = ["user", "user1", "new"]
            for index, ws in enumerate((user_ws, user1_ws, new_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])
                ws_message = ws.receive_json()
                self.assertEqual(ws_message["type"], MessageType.CHANGE_CHAT_NAME)
                self.assertEqual(ws_message["data"]["chat_name"], new_name)
                self.assertEqual(ws_message["data"]["chat_id"], TEST_CHAT_ID)

    def test_change_chat_name_not_auth(self):
        response = self.client.put(
            url=f"{self.chats_url}{TEST_CHAT_ID}",
            json={"chat_name": "новое название"}
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.NOT_AUTH_RESPONSE)

    def test_change_chat_name_empty_name(self):
        tokens = self.login()
        response = self.client.put(
            url=f"{self.chats_url}{TEST_CHAT_ID}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"chat_name": ""}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Укажите название чата"})

    def test_change_chat_name_same_name(self):
        tokens = self.login()
        response = self.client.put(
            url=f"{self.chats_url}{TEST_CHAT_ID}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"chat_name": TEST_CHAT_NAME}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Название чата совпадает с текущим"})

    def test_change_chat_name_not_exist_chat(self):
        tokens = self.login()
        response = self.client.put(
            url=f"{self.chats_url}bad_chat_id",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"chat_name": TEST_CHAT_NAME}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Чата с таким id не существует"})

    def test_change_chat_name_not_creator(self):
        not_creator = test_users[1]
        tokens = self.login(username=not_creator.login, password="password1")
        response = self.client.put(
            url=f"{self.chats_url}{TEST_CHAT_ID}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"chat_name": TEST_CHAT_NAME}
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "Изменить название чата может только создатель"})
