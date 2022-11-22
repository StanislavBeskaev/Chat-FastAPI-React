from starlette.testclient import WebSocketTestSession

from backend.services.ws.constants import MessageType, OnlineStatus

AUTHORIZATION = "Authorization"
BEARER = "Bearer"


class BaseTest:
    test_user_agent = "testclient"
    admin_login = "admin"
    admin_name = "Админ"
    admin_surname = "Админов"
    admin_password = "admin"
    NOT_AUTH_RESPONSE = {"detail": 'Not authenticated'}
    BAD_TOKEN_RESPONSE = {"detail": "Не валидный токен доступа"}
    BAD_CREDENTIALS = {"username": "user1", "password": "bad password"}
    BAD_PAYLOAD_REFRESH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NTQ3MDUwMDAsIm5iZiI6MTY1NDcwNTAwMCwiZXhwIjoyNjU0ODgwNTAwLCJraW5kIjoicmVmcmVzaCIsInVzZXIxIjp7Im5hbWUiOiLQkNC00LzQuNC9Iiwic3VybmFtZSI6ItCQ0LTQvNC40L3RgdC60LjQuSIsImxvZ2luIjoiYWRtaW4iLCJpZCI6MX19.OCxmfkyFUUvXab0Z6_fMLJFUGn7EG0LS3PmNGF-Dg2I"  # noqa
    DEFAULT_USER = "user"
    DEFAULT_PASSWORD = "user"

    @staticmethod
    def exception_response(message: str) -> dict[str, str]:
        return {"detail": message}

    @staticmethod
    def get_authorization_headers(username: str = DEFAULT_USER, password: str = DEFAULT_PASSWORD) -> dict:
        return {AUTHORIZATION: f"{BEARER} {username}-{password}"}

    @staticmethod
    def check_ws_online_status_notifications(ws: WebSocketTestSession, users: list[str]) -> None:
        """Проверка ws сообщений о входе пользователей в сеть"""
        for user in users:
            ws_message = ws.receive_json()
            assert ws_message["type"] == MessageType.STATUS
            assert ws_message["data"]["login"] == user
            assert ws_message["data"]["online_status"] == OnlineStatus.ONLINE
