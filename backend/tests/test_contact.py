from .. import models, tables
from ..services.auth import AuthService
from .base import BaseTestCase

test_users = [
    tables.User(login="user", name="user", surname="", password_hash=AuthService.hash_password("password")),
    tables.User(login="user1", name="user1", surname="", password_hash=AuthService.hash_password("password1")),
    tables.User(login="user2", name="user2", surname="", password_hash=AuthService.hash_password("password2")),
    tables.User(login="user3", name="user3", surname="", password_hash=AuthService.hash_password("password3")),
    tables.User(login="user4", name="user4", surname="", password_hash=AuthService.hash_password("password4")),
    tables.User(login="user5", name="user5", surname="", password_hash=AuthService.hash_password("password5")),
]


# TODO создание контактов для тестов

class TestContact(BaseTestCase):
    contacts_url = "/api/contacts/"

    def setUp(self) -> None:
        self.session.bulk_save_objects(test_users)
        self.session.commit()

    def tearDown(self) -> None:
        self.session.query(tables.User).delete()
        self.session.query(tables.RefreshToken).delete()
        self.session.commit()

    def _login(self) -> models.Tokens:
        login_response = self.client.post(
            "/api/auth/login",
            data={
                "username": "user",
                "password": "password"
            }
        )

        self.assertEqual(login_response.status_code, 200)
        tokens = models.Tokens.parse_obj(login_response.json())
        return tokens

    def test_add_wrong_token(self):
        response = self.client.post(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token="cool_token"),
            json={"login": "user"}
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Не валидный токен доступа"})

    def test_add_myself_to_contact(self):
        tokens = self._login()

        response = self.client.post(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": "user"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Нельзя добавить себя в контакты"})

    def test_add_not_exist_user(self):
        tokens = self._login()
        not_exist_user = "not_exist_user"

        response = self.client.post(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": not_exist_user}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": f"Пользователь с логином '{not_exist_user}' не найден"})

    # TODO тест на уже существующий контакт
    # TODO тест на успешное добавление контакта
