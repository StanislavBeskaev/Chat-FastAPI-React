from unittest.mock import patch

from backend import tables
from backend.dao.messages import MessagesDAO
from backend.dao.users import UsersDAO
from backend.services.auth import AuthService
from backend.services.ws.constants import MessageType, OnlineStatus, MESSAGE_TYPE_KEY, MESSAGE_DATA_KEY
from backend.tests.base import BaseTestCase, override_get_session


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


class TestInWSMessages(BaseTestCase):

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

        second_chat = tables.Chat(id=SECOND_CHAT_ID, name=SECOND_CHAT_NAME, creator_id=user.id)
        self.session.add(second_chat)
        second_chat_members = []
        for user in [user for user in users if user.login != "some"]:
            second_chat_members.append(tables.ChatMember(chat_id=SECOND_CHAT_ID, user_id=user.id))

        self.session.bulk_save_objects(second_chat_members)

        user_test_messages = [
            tables.Message(
                id=index,
                chat_id=TEST_CHAT_ID,
                text=text,
                user_id=user.id
            ) for index, text in enumerate(test_messages)
        ]
        user1 = next((user for user in users if user.login == "user1"))
        unread_messages = [
            tables.MessageReadStatus(message_id=message.id, user_id=user1.id)
            for message in user_test_messages
        ]
        self.session.bulk_save_objects(user_test_messages)
        self.session.bulk_save_objects(unread_messages)
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

    def test_statuses_messages(self):
        with self.client.websocket_connect("ws/user") as user_ws, \
                self.client.websocket_connect("ws/user1") as user1_ws,\
                self.client.websocket_connect("ws/new") as new_ws,\
                self.client.websocket_connect("ws/some") as some_ws:

            # Необходимо указывать пользователей в порядке подключения
            ws_users = ["user", "user1", "new", "some"]
            for index, ws in enumerate((user_ws, user1_ws, new_ws, some_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])

            user_ws.close()
            self._check_ws_offline_status_notification(
                ws_list=[user1_ws, new_ws, some_ws],
                disconnected_user="user"
            )

            new_ws.close()
            self._check_ws_offline_status_notification(
                ws_list=[user1_ws, some_ws],
                disconnected_user="new"
            )

            some_ws.close()
            self._check_ws_offline_status_notification(
                ws_list=[user1_ws],
                disconnected_user="some"
            )

    def _check_ws_offline_status_notification(self, ws_list, disconnected_user: str) -> None:
        for ws in ws_list:
            ws_message = ws.receive_json()
            self.assertEqual(ws_message["type"], MessageType.STATUS)
            self.assertEqual(ws_message["data"]["login"], disconnected_user)
            self.assertEqual(ws_message["data"]["online_status"], OnlineStatus.OFFLINE)

    def test_typing_messages(self):
        with self.client.websocket_connect("ws/user") as user_ws, \
                self.client.websocket_connect("ws/user1") as user1_ws,\
                self.client.websocket_connect("ws/new") as new_ws,\
                self.client.websocket_connect("ws/some") as some_ws:

            # Необходимо указывать пользователей в порядке подключения
            ws_users = ["user", "user1", "new", "some"]
            # Что бы прочитать статусные сообщения
            for index, ws in enumerate((user_ws, user1_ws, new_ws, some_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])

            user_ws.send_json(
                data={
                    MESSAGE_TYPE_KEY: MessageType.START_TYPING,
                    MESSAGE_DATA_KEY: {
                        "chatId": TEST_CHAT_ID
                    }
                }
            )
            self._check_ws_typing_notification(
                ws_list=[user_ws, user1_ws, new_ws, some_ws],
                user="user",
                typing_type=MessageType.START_TYPING,
                chat_id=TEST_CHAT_ID
            )

            user_ws.send_json(
                data={
                    MESSAGE_TYPE_KEY: MessageType.START_TYPING,
                    MESSAGE_DATA_KEY: {
                        "chatId": SECOND_CHAT_ID
                    }
                }
            )
            self._check_ws_typing_notification(
                ws_list=[user_ws, user1_ws, new_ws],
                user="user",
                typing_type=MessageType.START_TYPING,
                chat_id=SECOND_CHAT_ID
            )

            user_ws.send_json(
                data={
                    MESSAGE_TYPE_KEY: MessageType.STOP_TYPING,
                    MESSAGE_DATA_KEY: {
                        "chatId": TEST_CHAT_ID
                    }
                }
            )
            self._check_ws_typing_notification(
                ws_list=[user_ws, user1_ws, new_ws, some_ws],
                user="user",
                typing_type=MessageType.STOP_TYPING,
                chat_id=TEST_CHAT_ID
            )

    def _check_ws_typing_notification(self, ws_list, user: str, typing_type: str, chat_id: str) -> None:
        for ws in ws_list:
            ws_message = ws.receive_json()
            self.assertEqual(ws_message["type"], typing_type)
            self.assertEqual(ws_message["data"]["login"], user)
            self.assertEqual(ws_message["data"]["chat_id"], chat_id)

    def test_read_message(self):
        with self.client.websocket_connect("ws/user1") as user1_ws:
            user1_ws.send_json(
                data={
                    MESSAGE_TYPE_KEY: MessageType.READ_MESSAGE,
                    MESSAGE_DATA_KEY: {
                        "messageId": "0"
                    }
                }
            )

            import time
            time.sleep(0.5)  # Ожидание, что бы изменения ушли в базу
            messages_dao = MessagesDAO.create()
            users_dao = UsersDAO.create()
            message_read_status_after = messages_dao.get_unread_message(
                message_id="0",
                user_id=users_dao.find_user_by_login(login="user1").id
            )
            self.assertEqual(message_read_status_after.is_read, True)

    def test_text_message(self):
        with self.client.websocket_connect("ws/user") as user_ws, \
                self.client.websocket_connect("ws/user1") as user1_ws, \
                self.client.websocket_connect("ws/new") as new_ws, \
                self.client.websocket_connect("ws/some") as some_ws:
            # Необходимо указывать пользователей в порядке подключения
            ws_users = ["user", "user1", "new", "some"]
            for index, ws in enumerate((user_ws, user1_ws, new_ws, some_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])

            user_ws.send_json(
                data={
                    MESSAGE_TYPE_KEY: MessageType.TEXT,
                    MESSAGE_DATA_KEY: {
                        "text": "Новое сообщение",
                        "chatId": TEST_CHAT_ID
                    }
                }
            )
            self._check_ws_text_notification(
                ws_list=[user_ws, user1_ws, new_ws, some_ws],
                user="user",
                text="Новое сообщение",
                chat_id=TEST_CHAT_ID
            )

            user1_ws.send_json(
                data={
                    MESSAGE_TYPE_KEY: MessageType.TEXT,
                    MESSAGE_DATA_KEY: {
                        "text": "от первого",
                        "chatId": TEST_CHAT_ID
                    }
                }
            )
            self._check_ws_text_notification(
                ws_list=[user_ws, user1_ws, new_ws, some_ws],
                user="user1",
                text="от первого",
                chat_id=TEST_CHAT_ID
            )

            new_ws.send_json(
                data={
                    MESSAGE_TYPE_KEY: MessageType.TEXT,
                    MESSAGE_DATA_KEY: {
                        "text": "я тут",
                        "chatId": SECOND_CHAT_ID
                    }
                }
            )
            self._check_ws_text_notification(
                ws_list=[user_ws, user1_ws, new_ws],
                user="new",
                text="я тут",
                chat_id=SECOND_CHAT_ID
            )

    def _check_ws_text_notification(self, ws_list, user: str, text: str, chat_id: str):
        messages_dao = MessagesDAO.create()
        users_dao = UsersDAO.create()
        for ws in ws_list:
            ws_message = ws.receive_json()
            self.assertEqual(ws_message["type"], MessageType.TEXT)
            self.assertEqual(ws_message["data"]["login"], user)
            self.assertEqual(ws_message["data"]["chat_id"], chat_id)
            self.assertEqual(ws_message["data"]["text"], text)
            self.assertIsNotNone(ws_message["data"]["message_id"])

            message = messages_dao.get_message_by_id(message_id=ws_message["data"]["message_id"])
            self.assertIsNotNone(message)
            self.assertEqual(message.text, text)
            self.assertEqual(message.chat_id, chat_id)
            self.assertEqual(message.user_id, users_dao.find_user_by_login(login=user).id)
            self.assertEqual(message.type, MessageType.TEXT)
            self.assertIsNotNone(message.time)
            self.assertIsNone(message.change_time)
