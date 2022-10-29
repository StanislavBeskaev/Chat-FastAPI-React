from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession

from backend import models
from backend.services.ws.constants import MessageType, OnlineStatus


AUTHORIZATION = "Authorization"
BEARER = "Bearer"


class BaseTest:
    test_user_agent = "testclient"
    admin_login = "admin"
    admin_name = "Админ"
    admin_surname = "Админов"
    admin_password = "admin"
    # токен для user
    ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NjQ1NDczNjAsIm5iZiI6MTY2NDU0NzM2MCwiZXhwIjo2Nzc0NTQ4MjYwLCJraW5kIjoiYWNjZXNzIiwidXNlciI6eyJuYW1lIjoidXNlciIsInN1cm5hbWUiOiIiLCJsb2dpbiI6InVzZXIiLCJpZCI6MX19.BOlUb6VcNuHmYCy79uxwNxk522rQefKKhH_j7sNmtbU"  # noqa
    NOT_AUTH_RESPONSE = {"detail": 'Not authenticated'}
    BAD_TOKEN_RESPONSE = {"detail": "Не валидный токен доступа"}
    BAD_PAYLOAD_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NTQ3MDUwMDAsIm5iZiI6MTY1NDcwNTAwMCwiZXhwIjoyNzU0ODgwNTAwLCJraW5kIjoiYWNjZXNzIiwidXNlcjEiOnsibmFtZSI6ItCQ0LTQvNC40L0iLCJzdXJuYW1lIjoi0JDQtNC80LjQvdGB0LrQuNC5IiwibG9naW4iOiJhZG1pbiIsImlkIjoxfX0.D5PqBrHBVUeyvAWg7159sPxhQd2YS3-KTQZnF4tVlts"  # noqa
    BAD_PAYLOAD_REFRESH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NTQ3MDUwMDAsIm5iZiI6MTY1NDcwNTAwMCwiZXhwIjoyNjU0ODgwNTAwLCJraW5kIjoicmVmcmVzaCIsInVzZXIxIjp7Im5hbWUiOiLQkNC00LzQuNC9Iiwic3VybmFtZSI6ItCQ0LTQvNC40L3RgdC60LjQuSIsImxvZ2luIjoiYWRtaW4iLCJpZCI6MX19.OCxmfkyFUUvXab0Z6_fMLJFUGn7EG0LS3PmNGF-Dg2I"  # noqa
    DEFAULT_USER = "user"
    DEFAULT_PASSWORD = "password"

    @staticmethod
    def exception_response(message: str) -> dict[str, str]:
        return {"detail": message}

    @staticmethod
    def login(client: TestClient, username: str = DEFAULT_USER, password: str = DEFAULT_PASSWORD) -> models.Tokens:
        login_response = client.post("/api/auth/login", data={"username": username, "password": password})
        assert login_response.status_code == 200
        tokens = models.Tokens.parse_obj(login_response.json())
        return tokens

    @staticmethod
    def get_authorization_headers(access_token: str = ACCESS_TOKEN) -> dict:
        return {AUTHORIZATION: f"{BEARER} {access_token}"}

    @staticmethod
    def check_ws_online_status_notifications(ws: WebSocketTestSession, users: list[str]) -> None:
        """Проверка ws сообщений о входе пользователей в сеть"""
        for user in users:
            ws_message = ws.receive_json()
            assert ws_message["type"] == MessageType.STATUS
            assert ws_message["data"]["login"] == user
            assert ws_message["data"]["online_status"] == OnlineStatus.ONLINE
