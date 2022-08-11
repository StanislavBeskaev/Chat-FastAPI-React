from unittest.mock import patch

from backend import tables
from backend.services.auth import AuthService
from backend.tests.base import BaseTestCase, override_get_session, engine
from backend.services.ws.constants import MessageType


test_users = [
    tables.User(login="user", name="user", surname="", password_hash=AuthService.hash_password("password")),
    tables.User(login="user1", name="user1", surname="", password_hash=AuthService.hash_password("password1")),
    tables.User(login="new", name="new", surname="", password_hash=AuthService.hash_password("password2")),
]


class TestChats(BaseTestCase):
    chats_url = "/api/chats/"

    def setUp(self) -> None:
        tables.Base.metadata.create_all(bind=engine)
        self.session.bulk_save_objects(test_users)
        users = self.session.query(tables.User).all()

        profiles = []
        for user in users:
            profiles.append(tables.Profile(user=user.id, avatar_file=None))
        self.session.bulk_save_objects(profiles)
        self.session.commit()

        self.get_session_patcher = patch("backend.dao.get_session", return_value=override_get_session())
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
