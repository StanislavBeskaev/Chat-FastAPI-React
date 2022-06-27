from uuid import uuid4

from fastapi import UploadFile, HTTPException, status
from loguru import logger

from .. import models
from .. import tables
from . import BaseService
from .files import FilesService


class UserService(BaseService):
    """Сервис для управления пользователями"""

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

    def change_user_data(self, user_login: str, user_data: models.UserUpdate) -> models.User:
        """Изменение данных пользователя"""
        user = self.find_user_by_login(login=user_login)

        user.name = user_data.name
        user.surname = user_data.surname

        self.session.add(user)
        self.session.commit()
        logger.info(f"Изменение данных пользователя {user_login}, новые данные: {user_data}")

        return models.User.from_orm(user)

    def save_avatar(self, user: models.User, file: UploadFile) -> str:
        """Сохранение аватара для пользователя"""
        logger.debug(f"Запрос на сохранение аватара для пользователя {user}, файл: {file.filename}")
        files_service = FilesService()

        store_file_name = self._generate_avatar_file_name(file_name=file.filename)
        files_service.save_file(file=file, file_name=store_file_name)

        user_profile = self._find_profile_by_user_id(user_id=user.id)
        user_profile.avatar_file = store_file_name
        self.session.add(user_profile)
        self.session.commit()

        logger.info(f"Для пользователя {user} сохранён аватар {store_file_name}")
        return store_file_name

    def get_avatar(self, user: models.User) -> str | None:
        """Получение имени файла аватара пользователя"""
        user_profile = self._find_profile_by_user_id(user_id=user.id)

        logger.debug(f"Для пользователя {user}, файл аватара: {user_profile.avatar_file}")
        return user_profile.avatar_file

    def get_avatar_by_login(self, login: str) -> str | None:
        """Получение имени файла аватара пользователя по логину"""
        user_profile = self._find_profile_by_login(login=login)

        logger.debug(f"Для пользователя {user_profile.user}, файл аватара: {user_profile.avatar_file}")
        return user_profile.avatar_file

    def get_avatar_file_path_by_login(self, login: str) -> str:
        """Получение пути до аватара пользователя по логину"""
        avatar_file_name = self.get_avatar_by_login(login=login)
        if not avatar_file_name:
            return FilesService.get_no_avatar_file_path()

        avatar_file_path = FilesService.get_file_path(file_name=avatar_file_name)

        return avatar_file_path

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

    @staticmethod
    def _generate_avatar_file_name(file_name: str) -> str:
        """Получение имени файла для нового аватара"""
        file_extension = FilesService.get_file_extension(file_name=file_name)
        avatar_file_name = uuid4()

        result = f"{avatar_file_name}{file_extension}"
        logger.debug(f"Для файла {file_name}, сгенерировано имя для сохранения: {result}")
        return result

    def _find_profile_by_user_id(self, user_id: int) -> tables.Profile:
        """Нахождение профайла пользователя по id пользователя"""
        profile = (
            self.session
            .query(tables.Profile)
            .filter(tables.Profile.user == user_id)
            .first()
        )

        return profile

    def _find_profile_by_login(self, login: str) -> tables.Profile:
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
