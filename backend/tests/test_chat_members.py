from unittest.mock import patch

from backend import tables
from backend.services.auth import AuthService
from backend.tests.base import BaseTestCase, override_get_session
from backend.services.ws.constants import MessageType


test_users = [
    tables.User(login="user", name="user", surname="", password_hash=AuthService.hash_password("password")),
    tables.User(login="user1", name="user1", surname="", password_hash=AuthService.hash_password("password1")),
    tables.User(login="new", name="new", surname="", password_hash=AuthService.hash_password("password2")),
    tables.User(login="some", name="some", surname="", password_hash=AuthService.hash_password("password3")),
]
TEST_CHAT_ID = "TEST"
TEST_CHAT_NAME = "Тестовый чат"
SECOND_CHAT_ID = "SECOND"
SECOND_CHAT_NAME = "SECOND_CHAT"


class TestChatMembers(BaseTestCase):
    chat_members_url = "/api/chat_members/"

    def setUp(self) -> None:
        self.session.bulk_save_objects(test_users)
        users = self.session.query(tables.User).all()

        user = next((user for user in users if user.login == self.DEFAULT_USER))
        test_chat = tables.Chat(id=TEST_CHAT_ID, name=TEST_CHAT_NAME, creator_id=user.id)
        self.session.add(test_chat)
        second_chat = tables.Chat(id=SECOND_CHAT_ID, name=SECOND_CHAT_NAME, creator_id=user.id)
        self.session.add(second_chat)

        profiles = []
        test_chat_members = []
        for user in users:
            profiles.append(tables.Profile(user=user.id, avatar_file=None))
            if user.login not in ["user1", "some"]:
                test_chat_members.append(tables.ChatMember(chat_id=test_chat.id, user_id=user.id))
        self.session.bulk_save_objects(profiles)
        self.session.bulk_save_objects(test_chat_members)

        second_chat_members = []
        for user in [user for user in users if user.login != "some"]:
            second_chat_members.append(tables.ChatMember(chat_id=SECOND_CHAT_ID, user_id=user.id))
        self.session.bulk_save_objects(second_chat_members)

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

        self.get_session_patcher.stop()

    def test_success_add_chat_member(self):
        tokens = self.login()
        with self.client.websocket_connect("ws/user") as user_ws, \
                self.client.websocket_connect("ws/user1") as user1_ws,\
                self.client.websocket_connect("ws/new") as new_ws:

            # Необходимо указывать пользователей в порядке подключения
            ws_users = ["user", "user1", "new"]
            # Что бы прочитать статусные сообщения
            for index, ws in enumerate((user_ws, user1_ws, new_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])
            response = self.client.post(
                url=f"{self.chat_members_url}{TEST_CHAT_ID}",
                headers=self.get_authorization_headers(access_token=tokens.access_token),
                json={"login": "user1"}
            )
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {"message": f"Пользователь user1 добавлен к чату: {TEST_CHAT_ID}"})

            self._check_ws_add_to_chat_notifications(
                ws_list=[user_ws, user1_ws, new_ws],
                chat_id=TEST_CHAT_ID,
                action_user="user",
                user="user1",
                chat_name=TEST_CHAT_NAME
            )

    def _check_ws_add_to_chat_notifications(self, ws_list, chat_id: str, action_user: str, user: str, chat_name: str):
        for ws in ws_list:
            info_message = ws.receive_json()
            self.assertEqual(info_message["type"], MessageType.TEXT)
            self.assertEqual(info_message["data"]["login"], action_user)
            self.assertEqual(info_message["data"]["text"], f"{action_user} добавил пользователя {user}")
            self.assertIsNotNone(info_message["data"]["time"])
            self.assertEqual(info_message["data"]["chat_id"], chat_id)
            self.assertIsNotNone(info_message["data"]["message_id"])
            self.assertIsNotNone(info_message["data"]["type"], tables.MessageType.INFO)

            add_to_chat_message = ws.receive_json()
            self.assertEqual(add_to_chat_message["type"], MessageType.ADD_TO_CHAT)
            self.assertEqual(add_to_chat_message["data"]["login"], user)
            self.assertEqual(add_to_chat_message["data"]["chat_id"], chat_id)
            self.assertEqual(add_to_chat_message["data"]["chat_name"], chat_name)

    def test_add_chat_member_not_auth(self):
        response = self.client.post(
            url=f"{self.chat_members_url}{TEST_CHAT_ID}",
            json={"login": "user1"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.NOT_AUTH_RESPONSE)

    def test_add_chat_member_user_already_in_chat(self):
        tokens = self.login()
        candidate = "new"
        response = self.client.post(
            url=f"{self.chat_members_url}{TEST_CHAT_ID}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": candidate}
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {"detail": f"В чате {TEST_CHAT_ID} уже есть пользователь {candidate}"})

    def test_add_chat_members_not_exist_chat(self):
        tokens = self.login()
        candidate = "new"
        not_exist_chat_id = "bad_chat_id"
        response = self.client.post(
            url=f"{self.chat_members_url}{not_exist_chat_id}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": candidate}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": f"Чата с id {not_exist_chat_id} не существует"})

    def test_add_chat_member_by_not_chat_member(self):
        tokens = self.login(username="user1", password="password1")
        candidate = "new"
        response = self.client.post(
            url=f"{self.chat_members_url}{TEST_CHAT_ID}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": candidate}
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": f"Вы не участник чата {TEST_CHAT_ID}"})

    def test_add_chat_members_not_exist_login(self):
        tokens = self.login()
        not_exist_login = "bad_login"
        response = self.client.post(
            url=f"{self.chat_members_url}{TEST_CHAT_ID}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": not_exist_login}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": f"Пользователя с логином {not_exist_login} не существует"})

    def test_success_delete_chat_member(self):
        tokens = self.login()
        removable_user = "new"

        with self.client.websocket_connect("ws/user") as user_ws, \
                self.client.websocket_connect("ws/new") as new_ws:

            # Необходимо указывать пользователей в порядке подключения
            ws_users = ["user", "new"]
            # Что бы прочитать статусные сообщения
            for index, ws in enumerate((user_ws, new_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])

            response = self.client.delete(
                url=f"{self.chat_members_url}{TEST_CHAT_ID}",
                headers=self.get_authorization_headers(access_token=tokens.access_token),
                json={"login": removable_user}
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": f"Пользователь {removable_user} удалён из чата: {TEST_CHAT_ID}"})
            self._check_ws_delete_from_chat_message(
                ws_list=[user_ws, new_ws],
                chat_id=TEST_CHAT_ID,
                removable_user=removable_user,
                chat_name=TEST_CHAT_NAME
            )
            self._check_ws_delete_from_chat_info_message(
                ws_list=[user_ws],
                chat_id=TEST_CHAT_ID,
                action_user=self.DEFAULT_USER,
                removable_user=removable_user
            )

    def _check_ws_delete_from_chat_message(self, ws_list, chat_id: str, removable_user: str, chat_name: str):
        for ws in ws_list:
            delete_from_chat_message = ws.receive_json()
            self.assertEqual(delete_from_chat_message["type"], MessageType.DELETE_FROM_CHAT)
            self.assertEqual(delete_from_chat_message["data"]["login"], removable_user)
            self.assertEqual(delete_from_chat_message["data"]["chat_id"], chat_id)
            self.assertEqual(delete_from_chat_message["data"]["chat_name"], chat_name)

    def _check_ws_delete_from_chat_info_message(self, ws_list, chat_id: str, action_user: str, removable_user: str):
        for ws in ws_list:
            info_message = ws.receive_json()
            self.assertEqual(info_message["type"], MessageType.TEXT)
            self.assertEqual(info_message["data"]["login"], action_user)
            self.assertEqual(info_message["data"]["text"], f"{action_user} удалил пользователя {removable_user}")
            self.assertIsNotNone(info_message["data"]["time"])
            self.assertEqual(info_message["data"]["chat_id"], chat_id)
            self.assertIsNotNone(info_message["data"]["message_id"])
            self.assertEqual(info_message["data"]["type"], tables.MessageType.INFO)

    def test_delete_chat_member_not_auth(self):
        removable_user = "new"
        response = self.client.delete(
            url=f"{self.chat_members_url}{TEST_CHAT_ID}",
            json={"login": removable_user}
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.NOT_AUTH_RESPONSE)

    def test_delete_chat_member_user_not_in_chat(self):
        tokens = self.login()
        user_not_in_test_chat = "some"

        response = self.client.delete(
            url=f"{self.chat_members_url}{TEST_CHAT_ID}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": user_not_in_test_chat}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": f"Пользователя {user_not_in_test_chat} нет в чате"})

    def test_delete_chat_member_not_exist_chat(self):
        tokens = self.login()
        removable_user = "new"
        not_exist_chat_id = "not_exist_chat_id"

        response = self.client.delete(
            url=f"{self.chat_members_url}{not_exist_chat_id}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": removable_user}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": f"Чата с id {not_exist_chat_id} не существует"})

    def test_delete_chat_member_not_exist_login(self):
        tokens = self.login()
        not_exist_user = "bad_login"

        response = self.client.delete(
            url=f"{self.chat_members_url}{TEST_CHAT_ID}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": not_exist_user}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": f"Пользователя с логином {not_exist_user} не существует"})

    def test_delete_chat_member_by_not_chat_creator(self):
        tokens = self.login(username="new", password="password2")
        response = self.client.delete(
            url=f"{self.chat_members_url}{TEST_CHAT_ID}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": "new"}
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "Только создатель может удалять из чата"})

    def test_success_get_chat_members(self):
        tokens = self.login()
        response = self.client.get(
            url=f"{self.chat_members_url}{TEST_CHAT_ID}",
            headers=self.get_authorization_headers(access_token=tokens.access_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        for chat_member in response.json():
            self.assertIn(member=chat_member["login"], container=["user", "new"])
            self.assertFalse(chat_member["is_online"])

        with self.client.websocket_connect("ws/user"):
            response = self.client.get(
                url=f"{self.chat_members_url}{TEST_CHAT_ID}",
                headers=self.get_authorization_headers(access_token=tokens.access_token)
            )
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response.json(), list)
            for chat_member in response.json():
                self.assertIn(member=chat_member["login"], container=["user", "new"])
                if chat_member["login"] == "user":
                    self.assertTrue(chat_member["is_online"])
                else:
                    self.assertFalse(chat_member["is_online"])

    def test_get_chat_members_not_auth(self):
        response = self.client.get(
            url=f"{self.chat_members_url}{TEST_CHAT_ID}"
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.NOT_AUTH_RESPONSE)

    def test_get_chat_members_not_exist_chat(self):
        tokens = self.login()
        not_exist_chat_chat_id = "not_exist_chat_chat_id"
        response = self.client.get(
            url=f"{self.chat_members_url}{not_exist_chat_chat_id}",
            headers=self.get_authorization_headers(access_token=tokens.access_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": f"Чата с id {not_exist_chat_chat_id} не существует"})

    def test_get_chat_members_by_not_chat_member(self):
        tokens = self.login(username="user1", password="password1")
        response = self.client.get(
            url=f"{self.chat_members_url}{TEST_CHAT_ID}",
            headers=self.get_authorization_headers(access_token=tokens.access_token)
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": f"Вы не участник чата {TEST_CHAT_ID}"})
