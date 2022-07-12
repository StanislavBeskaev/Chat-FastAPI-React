from fastapi import HTTPException, status

from backend import tables, models
from backend.dao import BaseDAO


class UsersDAO(BaseDAO):
    """Класс для работы с пользователями в БД"""

    def find_user_by_login(self, login: str) -> tables.User | None:
        """Поиск пользователя по login"""
        user = (
            self.session
            .query(tables.User)
            .filter(tables.User.login == login)
            .first()
        )

        return user

    def find_user_by_id(self, user_id: int) -> tables.User | None:
        """Поиск пользователя по id"""
        user = (
            self.session
            .query(tables.User)
            .filter(tables.User.id == user_id)
            .first()
        )

        return user

    def get_user_info(self, login: str) -> models.User:
        user_info = (
            self.session
            .query(
                tables.User.id,
                tables.User.name,
                tables.User.surname,
            )
            .where(tables.User.login == login)
            .where(tables.User.id == tables.Profile.user)
            .first()
        )

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с логином '{login}' не найден"
            )

        return models.User(
            id=user_info[0],
            login=login,
            name=user_info[1],
            surname=user_info[2],
        )

    def change_user_data(self, login: str, name: str, surname: str) -> models.User:
        """Изменение данных пользователя"""
        user = self.find_user_by_login(login=login)

        user.name = name
        user.surname = surname
        self.session.add(user)
        self.session.commit()

        return models.User.from_orm(user)

    def find_profile_by_user_id(self, user_id: int) -> tables.Profile:
        """Нахождение профайла пользователя по id пользователя"""
        profile = (
            self.session
            .query(tables.Profile)
            .filter(tables.Profile.user == user_id)
            .first()
        )

        return profile

    def find_profile_by_login(self, login: str) -> tables.Profile:
        """Нахождение профайла пользователя по логину пользователя"""
        profile = (
            self.session
            .query(tables.Profile)
            .where(tables.Profile.user == tables.User.id)
            .where(tables.User.login == login)
            .first()
        )

        if not profile:
            raise HTTPException(status_code=404, detail=f"Пользователь с логином '{login}' не найден")

        return profile

    def set_avatar_file(self, user_id: int, avatar_file: str) -> None:
        """Установка имени файла аватара для пользователя"""
        user_profile = self.find_profile_by_user_id(user_id=user_id)
        user_profile.avatar_file = avatar_file
        self.session.add(user_profile)
        self.session.commit()
