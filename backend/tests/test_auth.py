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
