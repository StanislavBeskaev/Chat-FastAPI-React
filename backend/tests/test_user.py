import os
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.db.mock.facade import MockDBFacade
from backend.services.files import FilesService
from backend.settings import Settings
from backend.tests import data as test_data
from backend.tests.base import BaseTest


TEST_FILES_FOLDER = os.path.join(Path(__file__).resolve().parent, "files")


def get_settings_test_files_folder() -> Settings:
    return Settings(base_dir=Path(__file__).resolve().parent)


class TestUser(BaseTest):
    user_url = "/api/user"

    def test_success_get_user_info(self, client: TestClient):
        response = client.get(f"{self.user_url}/info/user2", headers=self.get_authorization_headers())
        assert response.status_code == 200
        assert response.json() == {"login": "user2", "name": "user2", "surname": "surname2", "id": 4}

    def test_get_user_info_not_exist_login(self, client: TestClient):
        response = client.get(f"{self.user_url}/info/not_exist_login", headers=self.get_authorization_headers())
        assert response.status_code == 404
        assert response.json() == self.exception_response("Пользователь с логином 'not_exist_login' не найден")

    def test_get_user_info_without_auth(self, client: TestClient):
        response = client.get(
            f"{self.user_url}/info/user2",
        )
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_get_user_info_wrong_access_token(self, client: TestClient):
        response = client.get(
            f"{self.user_url}/info/user2", headers=self.get_authorization_headers(access_token="bad.access.token")
        )
        assert response.status_code == 401
        assert response.json() == self.BAD_TOKEN_RESPONSE

    def test_success_change_user_data(self, client: TestClient, db_facade: MockDBFacade):
        new_name = "new_username"
        new_surname = "Иванов"

        response = client.put(
            f"{self.user_url}/change",
            headers=self.get_authorization_headers(),
            json={"name": new_name, "surname": new_surname},
        )
        assert response.status_code == 200

        our_user = db_facade.find_user_by_login(login="user")
        assert response.json() == {"id": our_user.id, "login": "user", "name": new_name, "surname": new_surname}
        assert our_user.name == new_name
        assert our_user.surname == new_surname

    def test_change_user_date_without_auth(self, client: TestClient):
        response = client.put(f"{self.user_url}/change", json={"name": "new_name", "surname": "new_surname"})
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_change_user_data_wrong_access_token(self, client: TestClient):
        response = client.put(
            f"{self.user_url}/change",
            headers=self.get_authorization_headers(access_token=self.BAD_PAYLOAD_ACCESS_TOKEN),
            json={"name": "new_name", "surname": "new_surname"},
        )
        assert response.status_code == 401
        assert response.json() == self.BAD_TOKEN_RESPONSE

    def test_success_upload_avatar(self, client: TestClient, db_facade: MockDBFacade):
        with open(os.path.join(TEST_FILES_FOLDER, "avatar_1.jpeg"), mode="rb") as file:
            response = client.post(
                f"{self.user_url}/avatar", headers=self.get_authorization_headers(), files={"file": file}
            )
        assert response.status_code == 201
        our_user_profile = db_facade.get_profile_by_login(login=self.DEFAULT_USER)
        assert our_user_profile.avatar_file == response.json()["avatar_file"]

    def test_upload_avatar_without_auth(self, client: TestClient):
        with open(os.path.join(TEST_FILES_FOLDER, "avatar_1.jpeg"), mode="rb") as file:
            response = client.post(f"{self.user_url}/avatar", files={"file": file})
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_upload_avatar_bad_access_token(self, client: TestClient):
        with open(os.path.join(TEST_FILES_FOLDER, "avatar_1.jpeg"), mode="rb") as file:
            response = client.post(
                f"{self.user_url}/avatar",
                headers=self.get_authorization_headers(access_token="bad.access.token"),
                files={"file": file},
            )
        assert response.status_code == 401
        assert response.json() == self.BAD_TOKEN_RESPONSE

    def test_success_get_login_avatar_filename(self, client: TestClient):
        response = client.get(url=f"{self.user_url}/avatar_file_name/user1", headers=self.get_authorization_headers())
        assert response.status_code == 200
        assert response.json() == {"avatar_file": "user1:surname1.jpeg"}

        response = client.get(url=f"{self.user_url}/avatar_file_name/user2", headers=self.get_authorization_headers())
        assert response.status_code == 200
        assert response.json() == {"avatar_file": ""}

    def test_get_login_avatar_filename_not_auth(self, client: TestClient):
        response = client.get(
            url=f"{self.user_url}/avatar_file_name/user1",
        )
        assert response.status_code == 401
        assert response.json() == self.NOT_AUTH_RESPONSE

    def test_get_login_avatar_filename_not_exist_login(self, client: TestClient):
        not_exist_login = "not_exist_login"
        response = client.get(
            url=f"{self.user_url}/avatar_file_name/{not_exist_login}", headers=self.get_authorization_headers()
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response(
            f"Профиль пользователя с логином '{not_exist_login}' не найден"
        )

    def test_success_get_login_avatar_file(self, client: TestClient):
        response = client.get(
            url=f"{self.user_url}/avatar_file/user2",
        )
        assert response.status_code == 200

        with open(FilesService.get_no_avatar_file_path(), mode="rb") as no_avatar_file:
            no_avatar_file_content = no_avatar_file.read()
            assert response.content == no_avatar_file_content

        get_settings_patcher = patch(target="backend.services.files.get_settings", new=get_settings_test_files_folder)
        get_settings_patcher.start()

        for user in test_data.users[:2]:
            response = client.get(
                url=f"{self.user_url}/avatar_file/{user.login}",
            )
            assert response.status_code == 200
            with open(os.path.join(TEST_FILES_FOLDER, f"{user.name}:{user.surname}.jpeg"), mode="rb") as avatar_file:
                user_avatar_file = avatar_file.read()
                assert response.content == user_avatar_file

        get_settings_patcher.stop()

    def test_get_login_avatar_file_not_exist_login(self, client: TestClient):
        not_exist_login = "not_exist_login"
        response = client.get(
            url=f"{self.user_url}/avatar_file/{not_exist_login}",
        )
        assert response.status_code == 404
        assert response.json() == self.exception_response(
            f"Профиль пользователя с логином '{not_exist_login}' не найден"
        )
