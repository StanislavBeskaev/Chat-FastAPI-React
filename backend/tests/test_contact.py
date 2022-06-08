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

contacts_users = ["user1", "user2", "user3"]


class TestContact(BaseTestCase):
    contacts_url = "/api/contacts/"

    def setUp(self) -> None:
        self.session.bulk_save_objects(test_users)
        users = self.session.query(tables.User).all()

        profiles = []
        for user in users:
            profiles.append(tables.Profile(user=user.id, avatar_file=None))
        self.session.bulk_save_objects(profiles)

        users_for_contacts: list[tables.User] = [user for user in users if user.login in contacts_users]
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
        self.session.query(tables.Contact).delete()
        self.session.query(tables.Profile).delete()
        self.session.query(tables.RefreshToken).delete()
        self.session.query(tables.User).delete()
        self.session.commit()

    def test_add_wrong_token(self):
        response = self.client.post(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token="cool_token"),
            json={"login": "user"}
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.BAD_TOKEN_RESPONSE)

    def test_add_myself_to_contact(self):
        tokens = self.login()

        response = self.client.post(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": "user"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Нельзя добавить себя в контакты"})

    def test_add_not_exist_user(self):
        tokens = self.login()
        not_exist_user = "not_exist_user"

        response = self.client.post(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": not_exist_user}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": f"Пользователь с логином '{not_exist_user}' не найден"})

    def test_success_add_contact(self):
        tokens = self.login()

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

        our_user = self.find_user_by_login(login="user")
        new_contact_user = self.find_user_by_login(login="user4")

        new_contact = self._find_contact(our_user_id=our_user.id, contact_user_id=new_contact_user.id)
        self.assertIsNotNone(new_contact)
        self.assertEqual(new_contact.name, "user4")
        self.assertEqual(new_contact.surname, "surname4")
        self.assertEqual(new_contact.owner_user_id, our_user.id)
        self.assertEqual(new_contact.contact_user_id, new_contact_user.id)

    def _find_contact(self, our_user_id: int, contact_user_id: int) -> tables.Contact | None:
        contact = (
            self.session
            .query(tables.Contact)
            .where(tables.Contact.owner_user_id == our_user_id)
            .where(tables.Contact.contact_user_id == contact_user_id)
            .first()
        )

        return contact

    def test_add_exist_contact(self):
        tokens = self.login()

        response = self.client.post(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": "user1"}
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {"detail": "Такой контакт уже существует"})

    def test_get_many_without_auth(self):
        response = self.client.get(
            self.contacts_url
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.NOT_AUTH_RESPONSE)

    def test_get_many_success(self):
        tokens = self.login()

        response = self.client.get(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "login": "user1",
                    "name": "user1",
                    "surname": "surname1",
                    "avatar_file": None
                },
                {
                    "login": "user2",
                    "name": "user2",
                    "surname": "surname2",
                    "avatar_file": None
                },
                {
                    "login": "user3",
                    "name": "user3",
                    "surname": "surname3",
                    "avatar_file": None
                },
            ]
        )

    def test_delete_not_auth(self):
        response = self.client.delete(
            self.contacts_url
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.NOT_AUTH_RESPONSE)

    def test_delete_miss_contact(self):
        tokens = self.login()

        response = self.client.delete(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token)
        )

        self.assertEqual(response.status_code, 422)

    def test_delete_not_exist_contact(self):
        tokens = self.login()

        response = self.client.delete(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": "user5"}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Контакт с логином 'user5' не найден"})

    def test_delete_not_exist_user(self):
        tokens = self.login()

        response = self.client.delete(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": "not_exist_user_login"}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Пользователь с логином 'not_exist_user_login' не найден"})

    def test_delete_success(self):
        tokens = self.login()

        response = self.client.delete(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={"login": "user3"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": f"Контакт user3 удалён"})

        our_user = self.find_user_by_login(login="user")
        self.assertIsNotNone(our_user)
        deleted_contact_user = self.find_user_by_login(login="user3")
        self.assertIsNotNone(deleted_contact_user)

        deleted_contact = self._find_contact(our_user_id=our_user.id, contact_user_id=deleted_contact_user.id)
        self.assertIsNone(deleted_contact)

    def test_get_one_not_auth(self):
        response = self.client.get(
            f"{self.contacts_url}user_1"
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.NOT_AUTH_RESPONSE)

    def test_get_one_not_exist_contact(self):
        tokens = self.login()

        response = self.client.get(
            f"{self.contacts_url}user5",
            headers=self.get_authorization_headers(access_token=tokens.access_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Контакт с логином 'user5' не найден"})

    def test_get_one_not_exist_user(self):
        tokens = self.login()

        response = self.client.get(
            f"{self.contacts_url}not_exist_user_login",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Пользователь с логином 'not_exist_user_login' не найден"})

    def test_get_one_success(self):
        tokens = self.login()

        response = self.client.get(
            f"{self.contacts_url}user1",
            headers=self.get_authorization_headers(access_token=tokens.access_token),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "login": "user1",
                "name": "user1",
                "surname": "surname1",
                "avatar_file": None
            }
        )

    def test_change_not_auth(self):
        response = self.client.put(
            self.contacts_url
        )

        self.assertEqual(response.status_code, 401)

    def test_change_bad_data(self):
        tokens = self.login()

        response = self.client.put(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={
                "name": "name",
                "surname": "surname"
            }
        )

        self.assertEqual(response.status_code, 422)

    def test_change_not_exist_contact(self):
        tokens = self.login()

        response = self.client.put(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={
                "login": "user5",
                "name": "name",
                "surname": "surname"
            }
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Контакт с логином 'user5' не найден"})

    def test_change_not_exist_user(self):
        tokens = self.login()

        response = self.client.put(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={
                "login": "not_exist_user_login",
                "name": "name",
                "surname": "surname"
            }
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Пользователь с логином 'not_exist_user_login' не найден"})

    def test_change_success(self):
        tokens = self.login()

        response = self.client.put(
            self.contacts_url,
            headers=self.get_authorization_headers(access_token=tokens.access_token),
            json={
                "login": "user1",
                "name": "Пользователь",
                "surname": "Первый"
            }
        )

        self.assertEqual(response.status_code, 204)

        our_user = self.find_user_by_login(login="user")
        self.assertIsNotNone(our_user)
        contact_user = self.find_user_by_login(login="user1")
        self.assertIsNotNone(contact_user)

        changed_contact = self._find_contact(our_user_id=our_user.id, contact_user_id=contact_user.id)
        self.assertIsNotNone(changed_contact)
        self.assertEqual(changed_contact.name, "Пользователь")
        self.assertEqual(changed_contact.surname, "Первый")
        self.assertEqual(changed_contact.owner_user_id, our_user.id)
        self.assertEqual(changed_contact.contact_user_id, contact_user.id)
