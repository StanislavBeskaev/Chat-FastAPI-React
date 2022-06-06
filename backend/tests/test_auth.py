from .. import models, tables
from ..api.auth import REFRESH_TOKEN_COOKIE_KEY
from ..services.auth import AuthService
from .base import BaseTestCase, override_get_session

test_users = [
    tables.User(login="user", name="user", surname="", password_hash=AuthService.hash_password("password")),
    tables.User(login="user1", name="user1", surname="", password_hash=AuthService.hash_password("password1")),
]


class TestAuth(BaseTestCase):
    auth_url = "/api/auth"

    def setUp(self) -> None:
        test_session = next(override_get_session())
        test_session.bulk_save_objects(test_users)
        test_session.commit()

    def tearDown(self) -> None:
        test_session = next(override_get_session())
        test_session.query(tables.User).delete()
        test_session.query(tables.RefreshToken).delete()
        test_session.commit()

    def test_success_registration(self):
        response = self.client.post(
            f"{self.auth_url}/registration",
            json={
                "login": "admin",
                "name": "Админ",
                "surname": "Админский",
                "password": "123"
            }
        )

        self.assertEqual(response.status_code, 201)

        tokens = models.Tokens.parse_obj(response.json())
        self.assertIn(member=REFRESH_TOKEN_COOKIE_KEY, container=response.cookies)

        refresh_token_in_db = (
            self.session
                .query(tables.RefreshToken.refresh_token)
                .where(tables.RefreshToken.refresh_token == tokens.refresh_token)
                .first()
        )
        self.assertIsNotNone(refresh_token_in_db)

    def test_user_already_exist_registration(self):
        response = self.client.post(
            f"{self.auth_url}/registration",
            json={
                "login": "user",
                "name": "Админ",
                "surname": "Админский",
                "password": "123"
            }
        )

        self.assertEqual(response.status_code, 409)

    def test_bad_request_registration(self):
        response = self.client.post(
            f"{self.auth_url}/registration",
            json={}
        )

        self.assertEqual(response.status_code, 422)

    def test_success_login(self):
        response = self.client.post(
            f"{self.auth_url}/login",
            data={
                "username": "user",
                "password": "password"
            }
        )

        self.assertEqual(response.status_code, 200)
        tokens = models.Tokens.parse_obj(response.json())
        self.assertIn(member=REFRESH_TOKEN_COOKIE_KEY, container=response.cookies)

        refresh_token_in_db = (
            self.session
                .query(tables.RefreshToken.refresh_token)
                .where(tables.RefreshToken.refresh_token == tokens.refresh_token)
                .first()
        )
        self.assertIsNotNone(refresh_token_in_db)

    def test_wrong_user_login(self):
        response = self.client.post(
            f"{self.auth_url}/login",
            data={
                "username": "user2",
                "password": "password"
            }
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Пользователь с таким логином не найден"})

    def test_wrong_password_login(self):
        response = self.client.post(
            f"{self.auth_url}/login",
            data={
                "username": "user",
                "password": "asd"
            }
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Неверный пароль"})

    def test_success_refresh(self):
        response = self.client.post(
            f"{self.auth_url}/login",
            data={
                "username": "user",
                "password": "password"
            }
        )

        self.assertEqual(response.status_code, 200)
        tokens = models.Tokens.parse_obj(response.json())

        refresh_response = self.client.get(
            f"{self.auth_url}/refresh",
            cookies={REFRESH_TOKEN_COOKIE_KEY: tokens.refresh_token}
        )

        self.assertEqual(refresh_response.status_code, 200)
        tokens = models.Tokens.parse_obj(refresh_response.json())

        self.assertIn(member=REFRESH_TOKEN_COOKIE_KEY, container=refresh_response.cookies)

        refresh_token_in_db = (
            self.session
            .query(tables.RefreshToken.refresh_token)
            .where(tables.RefreshToken.refresh_token == tokens.refresh_token)
            .first()
        )
        self.assertIsNotNone(refresh_token_in_db)

    def test_refresh_without_cookie(self):
        refresh_response = self.client.get(
            f"{self.auth_url}/refresh"
        )

        self.assertEqual(refresh_response.status_code, 401)

    def test_refresh_bad_cookie(self):
        refresh_response = self.client.get(
            f"{self.auth_url}/refresh",
            cookies={REFRESH_TOKEN_COOKIE_KEY: "maybeRefresh<-_->"}
        )

        self.assertEqual(refresh_response.status_code, 401)
        self.assertEqual(refresh_response.json(), {"detail": "Не валидный refresh_token"})

    def test_refresh_bad_miss_refresh_token_in_bd(self):
        response = self.client.post(
            f"{self.auth_url}/login",
            data={
                "username": "user",
                "password": "password"
            }
        )

        self.assertEqual(response.status_code, 200)
        tokens = models.Tokens.parse_obj(response.json())

        # Имитация, что из базы пропал refresh_token
        self.session.query(tables.RefreshToken).delete()
        self.session.commit()

        refresh_response = self.client.get(
            f"{self.auth_url}/refresh",
            cookies={REFRESH_TOKEN_COOKIE_KEY: tokens.refresh_token}
        )

        self.assertEqual(refresh_response.status_code, 401)
        self.assertEqual(refresh_response.json(), {"detail": "Не удалось обновить токены"})

    def test_refresh_wrong_user(self):
        response = self.client.post(
            f"{self.auth_url}/login",
            data={
                "username": "user",
                "password": "password"
            }
        )

        self.assertEqual(response.status_code, 200)
        tokens = models.Tokens.parse_obj(response.json())

        # Имитация, что из базы был удалён пользователь, для которого у нас есть refresh_token
        user_to_delete = self.session.query(tables.User).where(tables.User.login == "user").first()
        self.session.delete(user_to_delete)
        self.session.commit()

        refresh_response = self.client.get(
            f"{self.auth_url}/refresh",
            cookies={REFRESH_TOKEN_COOKIE_KEY: tokens.refresh_token}
        )

        self.assertEqual(refresh_response.status_code, 401)
        self.assertEqual(refresh_response.json(), {"detail": "Не удалось обновить токены"})

    # TODO тест logout
