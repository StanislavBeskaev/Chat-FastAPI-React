from .. import tables
from ..services.auth import AuthService
from .base import BaseTestCase

test_users = [
    tables.User(login="user", name="user", surname="surname", password_hash=AuthService.hash_password("password")),
    tables.User(login="user1", name="user1", surname="surname1", password_hash=AuthService.hash_password("password1")),
    tables.User(login="user2", name="user2", surname="surname2", password_hash=AuthService.hash_password("password2")),
    tables.User(login="user3", name="user3", surname="surname3", password_hash=AuthService.hash_password("password3")),
    tables.User(login="user4", name="user4", surname="surname4", password_hash=AuthService.hash_password("password4")),
    tables.User(login="user5", name="user5", surname="surname5", password_hash=AuthService.hash_password("password5")),
]


class TestContact(BaseTestCase):
    contacts_url = "/api/contacts/"

    def setUp(self) -> None:
        self.session.bulk_save_objects(test_users)
        users = self.session.query(tables.User).all()

        profiles = []
        for user in users:
            profiles.append(tables.Profile(user=user.id, avatar_file=None))
        self.session.bulk_save_objects(profiles)

        users_for_contacts: list[tables.User] = [user for user in users if user.login in ["user1", "user2", "user3"]]
        main_user = next((user for user in users if user.login == "user"))
        contacts = []
        for contact_user in users_for_contacts:
            contacts.append(tables.Contact(
                owner_user_id=main_user.id,
                contact_user_id=contact_user.id,
                name=contact_user.name,
                surname=contact_user.surname
            ))
        self.session.bulk_save_objects(contacts)
        self.session.commit()

    def tearDown(self) -> None:
        self.session.query(tables.User).delete()
        self.session.query(tables.RefreshToken).delete()
        self.session.commit()

    def test_add_wrong_token(self):
        response = self.client.post(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token="cool_token"),
            json={"login": "user"}
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Не валидный токен доступа"})

    def test_add_myself_to_contact(self):
        tokens = self.login(username="user", password="password")

        response = self.client.post(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": "user"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Нельзя добавить себя в контакты"})

    def test_add_not_exist_user(self):
        tokens = self.login(username="user", password="password")
        not_exist_user = "not_exist_user"

        response = self.client.post(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": not_exist_user}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": f"Пользователь с логином '{not_exist_user}' не найден"})

    def test_success_add_contact(self):
        tokens = self.login(username="user", password="password")

        response = self.client.post(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": "user4"}
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "login": "user4",
                "name": "user4",
                "surname": "surname4",
                "avatar_file": None
            }
        )

    def test_add_exist_contact(self):
        tokens = self.login(username="user", password="password")

        response = self.client.post(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": "user1"}
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {"detail": "Такой контакт уже существует"})
