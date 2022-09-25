from uuid import uuid4

from fastapi import UploadFile
from loguru import logger

from backend import models
from backend.services import BaseService
from backend.services.files import FilesService


class UserService(BaseService):
    """Сервис для управления пользователями"""

    @classmethod
    def is_admin(cls, user: models.User) -> bool:
        """Является ли пользователь админом"""
        return user.login == "admin"

    def change_user_data(self, user_login: str, user_data: models.UserUpdate) -> models.User:
        """Изменение данных пользователя"""
        user = self._db_facade.change_user_data(
            login=user_login,
            name=user_data.name,
            surname=user_data.surname
        )
        logger.info(f"Изменение данных пользователя {user_login}, новые данные: {user_data}")

        return user

    def save_avatar(self, user: models.User, file: UploadFile) -> str:
        """Сохранение аватара для пользователя"""
        logger.debug(f"Запрос на сохранение аватара для пользователя {user}, файл: {file.filename}")
        files_service = FilesService()

        store_file_name = self._generate_avatar_file_name(file_name=file.filename)
        files_service.save_file(file=file, file_name=store_file_name)

        self._db_facade.set_avatar_file(user_id=user.id, avatar_file=store_file_name)

        logger.info(f"Для пользователя {user} сохранён аватар {store_file_name}")
        return store_file_name

    def get_avatar_by_login(self, login: str) -> str | None:
        """Получение имени файла аватара пользователя по логину"""
        user_profile = self._db_facade.get_profile_by_login(login=login)

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
        """Получение информации о пользователе"""

        return self._db_facade.get_user_info(login=login)

    @staticmethod
    def _generate_avatar_file_name(file_name: str) -> str:
        """Получение имени файла для нового аватара"""
        file_extension = FilesService.get_file_extension(file_name=file_name)
        avatar_file_name = uuid4()

        result = f"{avatar_file_name}{file_extension}"
        logger.debug(f"Для файла {file_name}, сгенерировано имя для сохранения: {result}")
        return result
