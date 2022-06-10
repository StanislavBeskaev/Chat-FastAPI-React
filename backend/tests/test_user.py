from .. import tables
from ..services.auth import AuthService
from .base import BaseTestCase


test_users = [
    tables.User(login="user", name="user", surname="surname", password_hash=AuthService.hash_password("password")),
    tables.User(login="user1", name="user1", surname="surname1", password_hash=AuthService.hash_password("password1")),
    tables.User(login="user2", name="user2", surname="surname2", password_hash=AuthService.hash_password("password2")),
]


class TestUser(BaseTestCase):
    user_url = "/api/user"

    def setUp(self) -> None:
        self.session.bulk_save_objects(test_users)
        users = self.session.query(tables.User).all()
        profiles = []
        for user in users:
            profiles.append(tables.Profile(user=user.id, avatar_file=f"{user.name}:{user.surname}"))
        self.session.bulk_save_objects(profiles)
        self.session.commit()

    def tearDown(self) -> None:
        self.session.query(tables.Profile).delete()
        self.session.query(tables.RefreshToken).delete()
        self.session.query(tables.User).delete()
        self.session.commit()

    def test_success_get_avatar(self):
        tokens = self.login()

        response = self.client.get(
            f"{self.user_url}/avatar",
            headers=self.get_authorization_headers(access_token=tokens.access_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"avatar_file": "user:surname"})

    def test_get_avatar_without_auth(self):
        response = self.client.get(
            f"{self.user_url}/avatar",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.NOT_AUTH_RESPONSE)

    def test_get_avatar_wrong_access_token(self):
        response = self.client.get(
            f"{self.user_url}/avatar",
            headers=self.get_authorization_headers(access_token="bad.access.token")
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.BAD_TOKEN_RESPONSE)

    def test_success_get_login_avatar(self):
        tokens = self.login()
        response = self.client.get(
            f"{self.user_url}/avatar/user1",
            headers=self.get_authorization_headers(access_token=tokens.access_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"avatar_file": "user1:surname1"})

    def test_get_avatar_login_not_exist_login(self):
        tokens = self.login()
        response = self.client.get(
            f"{self.user_url}/avatar/not_exist_login",
            headers=self.get_authorization_headers(access_token=tokens.access_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Пользователь с логином 'not_exist_login' не найден"})

    def test_get_login_avatar_without_auth(self):
        response = self.client.get(
            f"{self.user_url}/avatar/user1",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.NOT_AUTH_RESPONSE)

    def test_get_login_avatar_wrong_access_token(self):
        response = self.client.get(
            f"{self.user_url}/avatar/user1",
            headers=self.get_authorization_headers(access_token="bad.access.token")
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.BAD_TOKEN_RESPONSE)

    def test_success_get_user_info(self):
        tokens = self.login()

        response = self.client.get(
            f"{self.user_url}/info/user2",
            headers=self.get_authorization_headers(access_token=tokens.access_token)
        )

        self.assertEqual(response.status_code, 200)

        requested_user = self.find_user_by_login("user2")
        self.assertEqual(
            response.json(),
            {
                "login": "user2",
                "name": "user2",
                "surname": "surname2",
                "id": requested_user.id,
                "avatar_file": "user2:surname2"
            }
        )

    def test_get_user_info_not_exist_login(self):
        tokens = self.login()

        response = self.client.get(
            f"{self.user_url}/info/not_exist_login",
            headers=self.get_authorization_headers(access_token=tokens.access_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Пользователь с логином 'not_exist_login' не найден"})

    def test_get_user_info_without_auth(self):
        response = self.client.get(
            f"{self.user_url}/info/user2",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.NOT_AUTH_RESPONSE)

    def test_get_user_info_wrong_access_token(self):
        response = self.client.get(
            f"{self.user_url}/info/user2",
            headers=self.get_authorization_headers(access_token="bad.access.token")
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.BAD_TOKEN_RESPONSE)

    def test_success_change_user_data(self):
        tokens = self.login()

        new_name = "new_username"
        new_surname = "Иванов"

        response = self.client.put(
            f"{self.user_url}/change",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={
                "name": new_name,
                "surname": new_surname
            }
        )

        self.assertEqual(response.status_code, 200)
        our_user = self.find_user_by_login(login="user")

        self.assertEqual(
            response.json(),
            {
                "id": our_user.id,
                "login": "user",
                "name": new_name,
                "surname": new_surname
            }
        )

        self.assertEqual(our_user.name, new_name)
        self.assertEqual(our_user.surname, new_surname)

    def test_change_user_date_without_auth(self):
        response = self.client.put(
            f"{self.user_url}/change",
            json={
                "name": "new_name",
                "surname": "new_surname"
            }
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.NOT_AUTH_RESPONSE)

    def test_change_user_data_wrong_access_token(self):
        response = self.client.put(
            f"{self.user_url}/change",
            headers=self.get_authorization_headers(access_token="bad.access.token"),
            json={
                "name": "new_name",
                "surname": "new_surname"
            }
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.BAD_TOKEN_RESPONSE)

    # TODO тесты upload_avatar
