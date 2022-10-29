from fastapi.testclient import TestClient

from backend.db.mock.facade import MockDBFacade
from backend.tests.base import BaseTest


class TestContact(BaseTest):
    contacts_url = "/api/contacts/"

    def test_success_add_contact(self, client: TestClient, db_facade: MockDBFacade):
        new_contact_username = "user4"
        response = client.post(
            self.contacts_url, headers=self.get_authorization_headers(), json={"login": new_contact_username}
        )
        assert response.status_code == 201
        assert response.json() == {"login": new_contact_username, "name": "user4", "surname": "surname4"}

        our_user = db_facade.find_user_by_login(login=self.DEFAULT_USER)
        new_contact_user = db_facade.find_user_by_login(login=new_contact_username)
        new_contact = db_facade.find_contact(owner_user_id=our_user.id, contact_user_id=new_contact_user.id)
        assert new_contact is not None
        assert new_contact.name == "user4"
        assert new_contact.surname == "surname4"
        assert new_contact.owner_user_id == our_user.id
        assert new_contact.contact_user_id == new_contact_user.id

    def test_add_wrong_token(self, client: TestClient):
        response = client.post(
            self.contacts_url, headers=self.get_authorization_headers(access_token="cool_token"), json={"login": "user"}
        )
        assert response.status_code == 401
        assert response.json() == self.BAD_TOKEN_RESPONSE

    def test_add_myself_to_contact(self, client: TestClient):
        response = client.post(self.contacts_url, headers=self.get_authorization_headers(), json={"login": "user"})
        assert response.status_code == 400
        assert response.json() == self.exception_response("Нельзя добавить себя в контакты")

    def test_add_not_exist_user(self, client: TestClient):
        not_exist_user = "not_exist_user"
        response = client.post(
            self.contacts_url, headers=self.get_authorization_headers(), json={"login": not_exist_user}
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response(f"Пользователь с логином '{not_exist_user}' не найден")

    def test_add_exist_contact(self, client: TestClient):
        response = client.post(self.contacts_url, headers=self.get_authorization_headers(), json={"login": "user1"})
        assert response.status_code == 409
        assert response.json() == self.exception_response("Такой контакт уже существует")

    def test_get_many_success(self, client: TestClient):
        response = client.get(self.contacts_url, headers=self.get_authorization_headers())
        assert response.status_code == 200
        assert response.json() == [
            {"login": "user1", "name": "user1", "surname": "surname1"},
            {"login": "user2", "name": "user2", "surname": "surname2"},
            {"login": "user3", "name": "user3", "surname": "surname3"},
        ]

    def test_get_many_without_auth(self, client: TestClient):
        response = client.get(self.contacts_url)
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_delete_success(self, client: TestClient, db_facade: MockDBFacade):
        deleted_user_login = "user3"
        response = client.delete(
            self.contacts_url, headers=self.get_authorization_headers(), json={"login": deleted_user_login}
        )
        assert response.status_code == 200
        assert response.json() == {"message": f"Контакт {deleted_user_login} удалён"}

        our_user = db_facade.find_user_by_login(login=self.DEFAULT_USER)
        assert our_user is not None

        deleted_contact_user = db_facade.find_user_by_login(login=deleted_user_login)
        assert deleted_contact_user is not None

        deleted_contact = db_facade.find_contact(owner_user_id=our_user.id, contact_user_id=deleted_contact_user.id)
        assert deleted_contact is None

    def test_delete_not_auth(self, client: TestClient):
        response = client.delete(self.contacts_url)
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_delete_miss_contact(self, client: TestClient):
        response = client.delete(self.contacts_url, headers=self.get_authorization_headers())
        assert response.status_code == 422

    def test_delete_not_exist_contact(self, client: TestClient):
        response = client.delete(self.contacts_url, headers=self.get_authorization_headers(), json={"login": "user5"})
        assert response.status_code == 404
        assert response.json() == self.exception_response("Контакт с логином 'user5' не найден")

    def test_delete_not_exist_user(self, client: TestClient):
        not_exist_user = "not_exist_user_login"
        response = client.delete(
            self.contacts_url, headers=self.get_authorization_headers(), json={"login": not_exist_user}
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response(f"Пользователь с логином '{not_exist_user}' не найден")

    def test_get_one_success(self, client: TestClient):
        response = client.get(
            f"{self.contacts_url}user1",
            headers=self.get_authorization_headers(),
        )
        assert response.status_code == 200
        assert response.json() == {"login": "user1", "name": "user1", "surname": "surname1"}

    def test_get_one_not_auth(self, client: TestClient):
        response = client.get(f"{self.contacts_url}user_1")
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_get_one_not_exist_contact(self, client: TestClient):
        response = client.get(f"{self.contacts_url}user5", headers=self.get_authorization_headers())
        assert response.status_code == 404
        assert response.json() == self.exception_response("Контакт с логином 'user5' не найден")

    def test_get_one_not_exist_user(self, client: TestClient):
        response = client.get(
            f"{self.contacts_url}not_exist_user_login",
            headers=self.get_authorization_headers(),
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response("Пользователь с логином 'not_exist_user_login' не найден")

    def test_change_success(self, client: TestClient, db_facade: MockDBFacade):
        changed_contact_user = "user1"
        response = client.put(
            self.contacts_url,
            headers=self.get_authorization_headers(),
            json={"login": changed_contact_user, "name": "Пользователь", "surname": "Первый"},
        )
        assert response.status_code == 200
        assert response.json() == {"message": f"Контакт user1 изменён"}

        our_user = db_facade.find_user_by_login(login=self.DEFAULT_USER)
        assert our_user is not None

        contact_user = db_facade.find_user_by_login(login=changed_contact_user)
        assert contact_user is not None

        changed_contact = db_facade.find_contact(owner_user_id=our_user.id, contact_user_id=contact_user.id)
        assert changed_contact is not None
        assert changed_contact.name == "Пользователь"
        assert changed_contact.surname == "Первый"
        assert changed_contact.owner_user_id == our_user.id
        assert changed_contact.contact_user_id == contact_user.id

    def test_change_not_auth(self, client: TestClient):
        response = client.put(self.contacts_url)
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_change_bad_data(self, client: TestClient):
        response = client.put(
            self.contacts_url, headers=self.get_authorization_headers(), json={"name": "name", "surname": "surname"}
        )
        assert response.status_code == 422

    def test_change_not_exist_contact(self, client: TestClient):
        response = client.put(
            self.contacts_url,
            headers=self.get_authorization_headers(),
            json={"login": "user5", "name": "name", "surname": "surname"},
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response("Контакт с логином 'user5' не найден")

    def test_change_not_exist_user(self, client: TestClient):
        response = client.put(
            self.contacts_url,
            headers=self.get_authorization_headers(),
            json={"login": "not_exist_user_login", "name": "name", "surname": "surname"},
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response("Пользователь с логином 'not_exist_user_login' не найден")
