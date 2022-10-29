from fastapi.testclient import TestClient
from requests.cookies import RequestsCookieJar

from backend import models
from backend.api.auth import REFRESH_TOKEN_COOKIE_KEY
from backend.db.mock.facade import MockDBFacade
from backend.settings import Settings
from backend.tests.base import BaseTest


class TestAuth(BaseTest):
    auth_url = "/api/auth"

    def test_success_registration(self, client: TestClient, db_facade: MockDBFacade, settings: Settings):
        response = client.post(
            f"{self.auth_url}/registration",
            json={
                "login": self.admin_login,
                "name": self.admin_name,
                "surname": self.admin_surname,
                "password": self.admin_password,
            },
        )
        assert response.status_code == 201
        assert REFRESH_TOKEN_COOKIE_KEY in response.cookies

        tokens = models.Tokens.parse_obj(response.json())
        refresh_token_in_db = db_facade.find_refresh_token_by_token(
            token=tokens.refresh_token, user_agent=self.test_user_agent
        )
        assert refresh_token_in_db is not None

        new_user = db_facade.find_user_by_login(login=self.admin_login)
        assert new_user is not None
        assert new_user.id is not None
        assert new_user.name == self.admin_name
        assert new_user.surname == self.admin_surname
        assert new_user.password_hash is not None

        new_user_profile = db_facade.get_profile_by_login(login=self.admin_login)
        assert new_user_profile is not None
        assert new_user_profile.avatar_file == ""

        new_user_main_chat_member = db_facade.find_chat_member(user_id=new_user.id, chat_id=settings.main_chat_id)
        assert new_user_main_chat_member is not None

    def test_user_already_exist_registration(self, client: TestClient):
        response = client.post(
            f"{self.auth_url}/registration",
            json={"login": self.DEFAULT_USER, "name": "Админ", "surname": "Админский", "password": "123"},
        )
        assert response.status_code == 409
        assert response.json() == self.exception_response("Пользователь с таким логином уже существует")

    def test_bad_request_registration(self, client: TestClient):
        response = client.post(f"{self.auth_url}/registration", json={})
        assert response.status_code == 422

    def test_success_login(self, client: TestClient, db_facade: MockDBFacade):
        response = client.post(
            f"{self.auth_url}/login", data={"username": self.DEFAULT_USER, "password": self.DEFAULT_PASSWORD}
        )
        assert response.status_code == 200

        tokens = models.Tokens.parse_obj(response.json())
        assert REFRESH_TOKEN_COOKIE_KEY in response.cookies

        refresh_token_in_db = db_facade.find_refresh_token_by_token(
            token=tokens.refresh_token, user_agent=self.test_user_agent
        )
        assert refresh_token_in_db is not None

    def test_wrong_user_login(self, client: TestClient):
        response = client.post(f"{self.auth_url}/login", data={"username": "bad_user", "password": "password"})
        assert response.status_code == 404
        assert response.json() == self.exception_response("Пользователь с таким логином не найден")

    def test_wrong_password_login(self, client: TestClient):
        response = client.post(f"{self.auth_url}/login", data={"username": self.DEFAULT_USER, "password": "asd"})
        assert response.status_code == 401
        assert response.json() == self.exception_response("Неверный пароль")

    def test_success_refresh(self, client: TestClient, db_facade: MockDBFacade):
        response = client.post(
            f"{self.auth_url}/login", data={"username": self.DEFAULT_USER, "password": self.DEFAULT_PASSWORD}
        )
        assert response.status_code == 200
        tokens = models.Tokens.parse_obj(response.json())

        refresh_response = client.get(
            f"{self.auth_url}/refresh", cookies={REFRESH_TOKEN_COOKIE_KEY: tokens.refresh_token}
        )
        assert response.status_code == 200
        tokens = models.Tokens.parse_obj(refresh_response.json())
        assert REFRESH_TOKEN_COOKIE_KEY in refresh_response.cookies

        refresh_token_in_db = db_facade.find_refresh_token_by_token(
            token=tokens.refresh_token, user_agent=self.test_user_agent
        )
        assert refresh_token_in_db is not None

    def test_refresh_without_cookie(self, client: TestClient):
        # Очистка cookie в клиенте, что бы не подхватился refresh token из другого запроса
        client.cookies = RequestsCookieJar()
        response = client.get(f"{self.auth_url}/refresh")
        assert response.status_code == 401
        assert response.json() == self.exception_response("Не валидный refresh_token")

    def test_refresh_bad_cookie(self, client: TestClient):
        response = client.get(f"{self.auth_url}/refresh", cookies={REFRESH_TOKEN_COOKIE_KEY: "maybeRefresh<-_->"})
        assert response.status_code == 401
        assert response.json() == self.exception_response("Не валидный refresh_token")

    def test_refresh_bad_payload_cookie(self, client: TestClient):
        response = client.get(
            f"{self.auth_url}/refresh", cookies={REFRESH_TOKEN_COOKIE_KEY: self.BAD_PAYLOAD_REFRESH_TOKEN}
        )
        assert response.status_code == 401
        assert response.json() == self.exception_response("Не валидный refresh_token")

    def test_refresh_bad_miss_refresh_token_in_bd(self, client: TestClient, db_facade: MockDBFacade):
        response = client.post(f"{self.auth_url}/login", data={"username": "user", "password": "password"})
        assert response.status_code == 200
        tokens = models.Tokens.parse_obj(response.json())

        # Имитация, что из базы пропал refresh_token
        db_facade.delete_all_refresh_tokens()

        refresh_response = client.get(
            f"{self.auth_url}/refresh", cookies={REFRESH_TOKEN_COOKIE_KEY: tokens.refresh_token}
        )
        assert refresh_response.status_code == 401
        assert refresh_response.json() == self.exception_response("Не удалось обновить токены")

    def test_refresh_wrong_user(self, client: TestClient, db_facade: MockDBFacade):
        response = client.post(
            f"{self.auth_url}/login", data={"username": self.DEFAULT_USER, "password": self.DEFAULT_PASSWORD}
        )
        assert response.status_code == 200
        tokens = models.Tokens.parse_obj(response.json())

        # Имитация, что из базы был удалён пользователь, для которого у нас есть refresh_token
        db_facade.delete_user_by_login(login=self.DEFAULT_USER)

        refresh_response = client.get(
            f"{self.auth_url}/refresh", cookies={REFRESH_TOKEN_COOKIE_KEY: tokens.refresh_token}
        )
        assert refresh_response.status_code == 401
        assert refresh_response.json() == self.exception_response("Не удалось обновить токены")

    def test_success_logout(self, client: TestClient):
        login_response = client.post(f"{self.auth_url}/login", data={"username": "user", "password": "password"})
        assert login_response.status_code == 200
        tokens = models.Tokens.parse_obj(login_response.json())

        logout_response = client.post(
            f"{self.auth_url}/logout", cookies={REFRESH_TOKEN_COOKIE_KEY: tokens.refresh_token}
        )
        assert login_response.status_code == 200
        assert logout_response.json() == {"message": "Выход из системы выполнен"}

    def test_logout_without_login(self, client: TestClient):
        response = client.post(f"{self.auth_url}/logout")
        assert response.status_code == 401
        assert response.json() == self.exception_response("Не валидный refresh_token")

    def test_logout_wrong_refresh_token(self, client: TestClient):
        response = client.post(f"{self.auth_url}/logout", cookies={REFRESH_TOKEN_COOKIE_KEY: "bad refresh token"})
        assert response.status_code == 401
        assert response.json() == self.exception_response("Не валидный refresh_token")
