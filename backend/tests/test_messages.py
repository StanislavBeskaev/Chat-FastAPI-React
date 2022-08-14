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
test_messages = ["Первое", "Как дела?", "куку"]
TEST_CHAT_ID = "TEST"
TEST_CHAT_NAME = "Тестовый чат"
SECOND_CHAT_ID = "SECOND"
SECOND_CHAT_NAME = "SECOND_CHAT"


class TestChats(BaseTestCase):
    messages_url = "/api/messages/"

    def setUp(self) -> None:
        self.session.bulk_save_objects(test_users)
        users = self.session.query(tables.User).all()

        user = next((user for user in users if user.login == self.DEFAULT_USER))
        test_chat = tables.Chat(id=TEST_CHAT_ID, name=TEST_CHAT_NAME, creator_id=user.id)
        self.session.add(test_chat)
        user_test_messages = [
            tables.Message(
                id=index,
                chat_id=TEST_CHAT_ID,
                text=text,
                user_id=user.id
            ) for index, text in enumerate(test_messages)
        ]
        self.session.bulk_save_objects(user_test_messages)

        profiles = []
        test_chat_members = []
        for user in users:
            profiles.append(tables.Profile(user=user.id, avatar_file=None))
            test_chat_members.append(tables.ChatMember(chat_id=test_chat.id, user_id=user.id))
        self.session.bulk_save_objects(profiles)
        self.session.bulk_save_objects(test_chat_members)

        second_chat = tables.Chat(id=SECOND_CHAT_ID, name=SECOND_CHAT_NAME, creator_id=user.id)
        self.session.add(second_chat)
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
        self.session.query(tables.MessageReadStatus).delete()
        self.session.query(tables.Message).delete()
        self.session.commit()

        self.get_session_patcher.stop()

    def test_success_change_message_text(self):
        tokens = self.login()
        change_message_id = "0"
        new_message_text = "Новый текст"

        with self.client.websocket_connect("ws/user") as user_ws, \
                self.client.websocket_connect("ws/user1") as user1_ws,\
                self.client.websocket_connect("ws/new") as new_ws,\
                self.client.websocket_connect("ws/some") as some_ws:

            # Необходимо указывать пользователей в порядке подключения
            ws_users = ["user", "user1", "new", "some"]
            # Что бы прочитать статусные сообщения
            for index, ws in enumerate((user_ws, user1_ws, new_ws, some_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])

            response = self.client.put(
                url=f"{self.messages_url}{change_message_id}",
                headers=self.get_authorization_headers(access_token=tokens.access_token),
                json={"text": new_message_text}
            )

            self.assertEqual(response.status_code, 200)
            self._check_ws_change_message_text_notification(
                ws_list=[user_ws, user1_ws, new_ws, some_ws],
                message_id=change_message_id,
                new_text=new_message_text,
                chat_id=TEST_CHAT_ID
            )

    def _check_ws_change_message_text_notification(self, ws_list, message_id: str, new_text: str, chat_id: str) -> None:
        for ws in ws_list:
            ws_message = ws.receive_json()
            self.assertEqual(ws_message["type"], MessageType.CHANGE_MESSAGE_TEXT)
            self.assertEqual(ws_message["data"]["chat_id"], chat_id)
            self.assertEqual(ws_message["data"]["message_id"], message_id)
            self.assertEqual(ws_message["data"]["text"], new_text)
            self.assertIsNotNone(ws_message["data"]["change_time"])

    def test_change_message_text_not_auth(self):
        change_message_id = "0"
        new_message_text = "Новый текст"
        response = self.client.put(
            url=f"{self.messages_url}{change_message_id}",
            json={"text": new_message_text}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.NOT_AUTH_RESPONSE)

    def test_change_message_text_empty_text(self):
        tokens = self.login()
        change_message_id = "0"
        new_message_text = ""

        response = self.client.put(
            url=f"{self.messages_url}{change_message_id}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"text": new_message_text}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Сообщение не может быть пустым"})

    def test_change_message_text_bad_message_id(self):
        tokens = self.login()
        bad_message_id = "bad_id"
        new_message_text = "Привет"

        response = self.client.put(
            url=f"{self.messages_url}{bad_message_id}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"text": new_message_text}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": f"Сообщение с id {bad_message_id} не найдено"})

    def test_change_message_text_not_owner(self):
        tokens = self.login(username="user1", password="password1")
        change_message_id = "0"
        new_message_text = "Новый текст"

        response = self.client.put(
            url=f"{self.messages_url}{change_message_id}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"text": new_message_text}
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "Только автор может менять сообщение!"})

    def test_change_message_text_same_text(self):
        tokens = self.login()
        change_message_id = "0"
        same_message_text = test_messages[0]

        response = self.client.put(
            url=f"{self.messages_url}{change_message_id}",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"text": same_message_text}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "У сообщения уже такой текст"})
