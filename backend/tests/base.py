import os
from pathlib import Path
from typing import Generator
from unittest import TestCase

from fastapi.testclient import TestClient
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend import tables, models
from backend.database import get_session
from backend.main import app
from backend.services.ws.constants import MessageType, OnlineStatus


TEST_DB_NAME = "test.db"
TEST_SQLALCHEMY_DATABASE_URL = f"sqlite:///./{TEST_DB_NAME}"
AUTHORIZATION = "Authorization"
BEARER = "Bearer"

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_session() -> Generator[Session, None, None]:
    test_session = TestingSessionLocal()
    try:
        yield test_session
    finally:
        try:
            test_session.close()
        except:
            pass


class BaseTestCase(TestCase):
    client = TestClient(app)
    session = next(override_get_session())
    NOT_AUTH_RESPONSE = {"detail": 'Not authenticated'}
    BAD_TOKEN_RESPONSE = {"detail": "Не валидный токен доступа"}
    BAD_PAYLOAD_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NTQ3MDUwMDAsIm5iZiI6MTY1NDcwNTAwMCwiZXhwIjoyNzU0ODgwNTAwLCJraW5kIjoiYWNjZXNzIiwidXNlcjEiOnsibmFtZSI6ItCQ0LTQvNC40L0iLCJzdXJuYW1lIjoi0JDQtNC80LjQvdGB0LrQuNC5IiwibG9naW4iOiJhZG1pbiIsImlkIjoxfX0.D5PqBrHBVUeyvAWg7159sPxhQd2YS3-KTQZnF4tVlts"
    BAD_PAYLOAD_REFRESH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NTQ3MDUwMDAsIm5iZiI6MTY1NDcwNTAwMCwiZXhwIjoyNjU0ODgwNTAwLCJraW5kIjoicmVmcmVzaCIsInVzZXIxIjp7Im5hbWUiOiLQkNC00LzQuNC9Iiwic3VybmFtZSI6ItCQ0LTQvNC40L3RgdC60LjQuSIsImxvZ2luIjoiYWRtaW4iLCJpZCI6MX19.OCxmfkyFUUvXab0Z6_fMLJFUGn7EG0LS3PmNGF-Dg2I"
    DEFAULT_USER = "user"
    DEFAULT_PASSWORD = "password"

    @classmethod
    def setUpClass(cls) -> None:
        cls._drop_test_db()
        app.dependency_overrides[get_session] = override_get_session
        tables.Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls) -> None:
        app.dependency_overrides = {}

    @staticmethod
    def _drop_test_db():
        test_db_file_path = os.path.join(Path(__file__).resolve().parent.parent.parent, TEST_DB_NAME)
        if os.path.exists(test_db_file_path):
            os.remove(test_db_file_path)
            logger.info(f"Удалён файл тестовой базы: {test_db_file_path}")

    @staticmethod
    def get_authorization_headers(access_token: str) -> dict:
        return {AUTHORIZATION: f"{BEARER} {access_token}"}

    def login(self, username: str = DEFAULT_USER, password: str = DEFAULT_PASSWORD) -> models.Tokens:
        login_response = self.client.post(
            "/api/auth/login",
            data={
                "username": username,
                "password": password
            }
        )

        self.assertEqual(login_response.status_code, 200)
        tokens = models.Tokens.parse_obj(login_response.json())
        return tokens

    def find_user_by_login(self, login: str) -> tables.User | None:
        """Поиск пользователя по login"""
        user = (
            self.session
            .query(tables.User)
            .filter(tables.User.login == login)
            .first()
        )

        return user

    def check_ws_online_status_notifications(self, ws, users: list[str]) -> None:
        """Проверка ws сообщений о входе пользователей в сеть"""
        for user in users:
            ws_message = ws.receive_json()
            self.assertEqual(ws_message["type"], MessageType.STATUS)
            self.assertEqual(ws_message["data"]["login"], user)
            self.assertEqual(ws_message["data"]["online_status"], OnlineStatus.ONLINE)
