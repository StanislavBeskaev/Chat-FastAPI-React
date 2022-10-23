from fastapi import HTTPException

from backend import models, tables
from backend.core.decorators import model_result


class MockUsersDAO:
    """Mock класс для работы с пользователями в БД"""
    users: list[tables.User]
    profiles: list[tables.Profile]

    def delete_user_by_login(self, login: str) -> None:
        """Удаление пользователя. Нужно для тестов"""
        self.users = [user for user in self.users if user.login != login]

    @model_result(models.UserWithPassword)
    def get_all_users(self) -> list[models.User]:
        """Получение всех записей таблицы пользователей"""
        return self.users

    @model_result(models.Profile)
    def get_all_profiles(self) -> list[models.Profile]:
        """Получение всех записей таблицы профилей"""
        return self.profiles

    def create_user(self, login: str, password_hash: str, name: str, surname: str) -> models.User:
        """Создание пользователя"""
        new_user = tables.User(
            id=max([user.id for user in self.users]) + 1,
            login=login,
            password_hash=password_hash,
            name=name,
            surname=surname
        )
        self.users.append(new_user)
        new_user = models.User.from_orm(new_user)
        return new_user

    def create_user_profile(self, user_id) -> None:
        """Создание профиля для пользователя"""
        user_profile = tables.Profile(
            id=max([profile.id for profile in self.profiles]) + 1,
            user=user_id,
            avatar_file=""
        )
        self.profiles.append(user_profile)

    def find_user_by_login(self, login: str) -> tables.User | None:
        """Поиск пользователя по login"""
        user = next(
            (user for user in self.users if user.login == login),
            None
        )
        return user

    def find_user_by_id(self, user_id: int) -> tables.User | None:
        """Поиск пользователя по id"""
        user = next(
            (user for user in self.users if user.id == user_id),
            None
        )
        return user

    @model_result(models.User)
    def get_user_info(self, login: str) -> models.User:
        """Получение информации и пользователе"""
        user_info = self.find_user_by_login(login=login)

        if not user_info:
            raise HTTPException(status_code=404, detail=f"Пользователь с логином '{login}' не найден")

        return user_info

    @model_result(models.User)
    def change_user_data(self, login: str, name: str, surname: str) -> models.User:
        """Изменение данных пользователя"""
        user = self.find_user_by_login(login=login)
        user.name = name
        user.surname = surname
        return user

    @model_result(models.Profile)
    def get_profile_by_login(self, login: str) -> models.Profile:
        """Нахождение профайла пользователя по логину пользователя"""
        exception = HTTPException(status_code=404, detail=f"Профиль пользователя с логином '{login}' не найден")
        user = self.find_user_by_login(login=login)
        if not user:
            raise exception

        profile = next(
            (profile for profile in self.profiles if profile.user == user.id)
        )

        if not profile:
            raise HTTPException(status_code=404, detail=f"Профиль пользователя с логином '{login}' не найден")

        return profile

    def set_avatar_file(self, user_id: int, avatar_file: str) -> None:
        """Установка имени файла аватара для пользователя"""
        user_profile = self._find_profile_by_user_id(user_id=user_id)
        user_profile.avatar_file = avatar_file

    def get_used_avatar_files(self) -> list[str]:
        """Получение названий используемых файлов аватаров"""
        avatar_files = [
            profile.avatar_file for profile in self.profiles
        ]
        return avatar_files

    def _find_profile_by_user_id(self, user_id: int) -> tables.Profile:
        user = self.find_user_by_id(user_id=user_id)
        profile = next(
            (profile for profile in self.profiles if profile.user == user.id)
        )
        return profile
