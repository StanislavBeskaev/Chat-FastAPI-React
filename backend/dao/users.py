from fastapi import HTTPException
from loguru import logger

from backend import tables, models
from backend.dao import BaseDAO


class UsersDAO(BaseDAO):
    """Класс для работы с пользователями в БД"""

    def create_user(self, login: str, password_hash: str, name: str, surname: str) -> models.User:
        """Создание пользователя"""
        new_user = tables.User(
            login=login,
            password_hash=password_hash,
            name=name,
            surname=surname
        )

        self.session.add(new_user)
        self.session.commit()

        new_user = models.User.from_orm(new_user)
        logger.info(f"Создан новый пользователь: {new_user}")

        return new_user

    def create_user_profile(self, user_id) -> None:
        """Создание профиля для пользователя"""
        user_profile = tables.Profile(user=user_id)
        self.session.add(user_profile)
        self.session.commit()
        logger.debug(f"Создан профиль для пользователя {user_id}")

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
        """Получение информации и пользователе"""
        user_info = self.find_user_by_login(login=login)

        if not user_info:
            raise HTTPException(status_code=404, detail=f"Пользователь с логином '{login}' не найден")

        return models.User.from_orm(user_info)

    def change_user_data(self, login: str, name: str, surname: str) -> models.User:
        """Изменение данных пользователя"""
        user = self.find_user_by_login(login=login)

        user.name = name
        user.surname = surname
        self.session.add(user)
        self.session.commit()

        return models.User.from_orm(user)

    def get_profile_by_login(self, login: str) -> models.Profile:
        """Нахождение профайла пользователя по логину пользователя"""
        db_profile = (
            self.session
            .query(tables.Profile)
            .where(tables.Profile.user == tables.User.id)
            .where(tables.User.login == login)
            .first()
        )

        if not db_profile:
            raise HTTPException(status_code=404, detail=f"Профиль пользователя с логином '{login}' не найден")

        return models.Profile.from_orm(db_profile)

    def set_avatar_file(self, user_id: int, avatar_file: str) -> None:
        """Установка имени файла аватара для пользователя"""
        user_profile = self._find_profile_by_user_id(user_id=user_id)
        user_profile.avatar_file = avatar_file
        self.session.add(user_profile)
        self.session.commit()

    def _find_profile_by_user_id(self, user_id: int) -> tables.Profile:
        db_profile = (
            self.session
                .query(tables.Profile)
                .filter(tables.Profile.user == user_id)
                .first()
        )
        return db_profile
