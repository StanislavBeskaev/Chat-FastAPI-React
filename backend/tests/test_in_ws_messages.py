from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession

from backend.db.mock.facade import MockDBFacade
from backend.services.ws.constants import MESSAGE_DATA_KEY, MESSAGE_TYPE_KEY, MessageType, OnlineStatus
from backend.tests import data as test_data
from backend.tests.base import BaseTest


class TestInWSMessages(BaseTest):
    def test_statuses_messages(self, client: TestClient):
        with client.websocket_connect("ws/user") as user_ws, client.websocket_connect(
            "ws/user1"
        ) as user1_ws, client.websocket_connect("ws/new") as new_ws, client.websocket_connect("ws/some") as some_ws:

            # Необходимо указывать пользователей в порядке подключения
            ws_users = ["user", "user1", "new", "some"]
            for index, ws in enumerate((user_ws, user1_ws, new_ws, some_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])

            user_ws.close()
            self._check_ws_offline_status_notification(ws_list=[user1_ws, new_ws, some_ws], disconnected_user="user")

            new_ws.close()
            self._check_ws_offline_status_notification(ws_list=[user1_ws, some_ws], disconnected_user="new")

            some_ws.close()
            self._check_ws_offline_status_notification(ws_list=[user1_ws], disconnected_user="some")

    @staticmethod
    def _check_ws_offline_status_notification(ws_list: list[WebSocketTestSession], disconnected_user: str) -> None:
        for ws in ws_list:
            ws_message = ws.receive_json()
            assert ws_message[MESSAGE_TYPE_KEY] == MessageType.STATUS
            assert ws_message[MESSAGE_DATA_KEY]["login"] == disconnected_user
            assert ws_message["data"]["online_status"] == OnlineStatus.OFFLINE

    def test_typing_messages(self, client: TestClient):
        with client.websocket_connect("ws/user") as user_ws, client.websocket_connect(
            "ws/user1"
        ) as user1_ws, client.websocket_connect("ws/new") as new_ws, client.websocket_connect("ws/user2") as user2_ws:

            # Необходимо указывать пользователей в порядке подключения
            ws_users = ["user", "user1", "new", "user2"]
            # Что бы прочитать статусные сообщения
            for index, ws in enumerate((user_ws, user1_ws, new_ws, user2_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])

            user_ws.send_json(
                data={MESSAGE_TYPE_KEY: MessageType.START_TYPING, MESSAGE_DATA_KEY: {"chatId": test_data.TEST_CHAT_ID}}
            )
            self._check_ws_typing_notification(
                ws_list=[user_ws, user1_ws, new_ws],
                user="user",
                typing_type=MessageType.START_TYPING,
                chat_id=test_data.TEST_CHAT_ID,
            )

            user_ws.send_json(
                data={
                    MESSAGE_TYPE_KEY: MessageType.START_TYPING,
                    MESSAGE_DATA_KEY: {"chatId": test_data.SECOND_CHAT_ID},
                }
            )
            self._check_ws_typing_notification(
                ws_list=[user_ws, user1_ws, new_ws, user2_ws],
                user="user",
                typing_type=MessageType.START_TYPING,
                chat_id=test_data.SECOND_CHAT_ID,
            )

            user_ws.send_json(
                data={MESSAGE_TYPE_KEY: MessageType.STOP_TYPING, MESSAGE_DATA_KEY: {"chatId": test_data.TEST_CHAT_ID}}
            )
            self._check_ws_typing_notification(
                ws_list=[user_ws, user1_ws, new_ws],
                user="user",
                typing_type=MessageType.STOP_TYPING,
                chat_id=test_data.TEST_CHAT_ID,
            )

            user_ws.send_json(
                data={MESSAGE_TYPE_KEY: MessageType.STOP_TYPING, MESSAGE_DATA_KEY: {"chatId": test_data.SECOND_CHAT_ID}}
            )
            self._check_ws_typing_notification(
                ws_list=[user_ws, user1_ws, new_ws, user2_ws],
                user="user",
                typing_type=MessageType.STOP_TYPING,
                chat_id=test_data.SECOND_CHAT_ID,
            )

    @staticmethod
    def _check_ws_typing_notification(
        ws_list: list[WebSocketTestSession], user: str, typing_type: str, chat_id: str
    ) -> None:
        for ws in ws_list:
            ws_message = ws.receive_json()
            assert ws_message[MESSAGE_TYPE_KEY] == typing_type
            assert ws_message[MESSAGE_DATA_KEY]["login"] == user
            assert ws_message[MESSAGE_DATA_KEY]["chat_id"] == chat_id

    def test_read_message(self, client: TestClient, db_facade: MockDBFacade):
        with client.websocket_connect("ws/user1") as user1_ws:
            message_read_status_before = db_facade.get_unread_message(message_id="1", user_id=2)
            assert message_read_status_before.is_read is False
            user1_ws.send_json(data={MESSAGE_TYPE_KEY: MessageType.READ_MESSAGE, MESSAGE_DATA_KEY: {"messageId": "1"}})
            import time

            # прочтение сообщение асинхронное действие, немного подождём результат
            time.sleep(0.1)
            message_read_status_after = db_facade.get_unread_message(message_id="1", user_id=2)
            assert message_read_status_after.is_read is True

            # Попытка прочитать не существующее сообщение
            user1_ws.send_json(
                data={MESSAGE_TYPE_KEY: MessageType.READ_MESSAGE, MESSAGE_DATA_KEY: {"messageId": "bad_message_id"}}
            )

    def test_text_message(self, client: TestClient, db_facade: MockDBFacade):
        with client.websocket_connect("ws/user") as user_ws, client.websocket_connect(
            "ws/user1"
        ) as user1_ws, client.websocket_connect("ws/new") as new_ws:
            # Необходимо указывать пользователей в порядке подключения
            ws_users = ["user", "user1", "new"]
            for index, ws in enumerate((user_ws, user1_ws, new_ws)):
                self.check_ws_online_status_notifications(ws=ws, users=ws_users[index:])

            user_ws.send_json(
                data={
                    MESSAGE_TYPE_KEY: MessageType.TEXT,
                    MESSAGE_DATA_KEY: {"text": "Новое сообщение", "chatId": test_data.TEST_CHAT_ID},
                }
            )
            self._check_ws_text_notification(
                ws_list=[user_ws, user1_ws, new_ws],
                user="user",
                text="Новое сообщение",
                chat_id=test_data.TEST_CHAT_ID,
                db_facade=db_facade,
            )

            user1_ws.send_json(
                data={
                    MESSAGE_TYPE_KEY: MessageType.TEXT,
                    MESSAGE_DATA_KEY: {"text": "от первого", "chatId": test_data.TEST_CHAT_ID},
                }
            )
            self._check_ws_text_notification(
                ws_list=[user_ws, user1_ws, new_ws],
                user="user1",
                text="от первого",
                chat_id=test_data.TEST_CHAT_ID,
                db_facade=db_facade,
            )

            new_ws.send_json(
                data={
                    MESSAGE_TYPE_KEY: MessageType.TEXT,
                    MESSAGE_DATA_KEY: {"text": "я тут", "chatId": test_data.SECOND_CHAT_ID},
                }
            )
            self._check_ws_text_notification(
                ws_list=[user_ws, user1_ws, new_ws],
                user="new",
                text="я тут",
                chat_id=test_data.SECOND_CHAT_ID,
                db_facade=db_facade,
            )

    @staticmethod
    def _check_ws_text_notification(
        ws_list: list[WebSocketTestSession], user: str, text: str, chat_id: str, db_facade: MockDBFacade
    ):
        for ws in ws_list:
            ws_message = ws.receive_json()
            assert ws_message["type"] == MessageType.TEXT
            assert ws_message["data"]["login"] == user
            assert ws_message["data"]["chat_id"] == chat_id
            assert ws_message["data"]["text"] == text
            assert ws_message["data"]["message_id"] is not None

            message = db_facade.get_message_by_id(message_id=ws_message["data"]["message_id"])
            assert message.text == text
            assert message.chat_id == chat_id
            assert message.user_id == db_facade.find_user_by_login(login=user).id
            assert message.type == MessageType.TEXT
            assert message.time is not None
            assert message.change_time is None
