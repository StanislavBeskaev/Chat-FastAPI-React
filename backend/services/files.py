import os
from fastapi import UploadFile
from loguru import logger

from backend import tables
from backend.db_config import get_session
from backend.settings import get_settings


FILES_FOLDER = "files"
IMAGES_FOLDER = "images"
NO_AVATAR_FILE = "no_avatar.png"


def check_files_folder(func):
    """Декоратор для создания папки под файлы, если папки нет"""
    def wrapper(*args, **kwargs):
        files_folder = os.path.join(get_settings().base_dir, FILES_FOLDER)
        if not os.path.exists(files_folder):
            logger.info(f"Создана папка под файлы {files_folder}")
            os.mkdir(files_folder)

        return func(*args, **kwargs)

    return wrapper


class FilesService:
    """Сервис для управления файлами"""

    @classmethod
    def get_file_extension(cls, file_name) -> str:
        """Получение расширения файла"""
        filename, file_extension = os.path.splitext(file_name)

        return file_extension

    @check_files_folder
    def save_file(self, file: UploadFile, file_name: str) -> str:
        """Сохранение файла"""
        file_path = self.get_file_path(file_name)
        with open(file_path, mode="wb") as writable_file:
            writable_file.write(file.file.read())

        logger.debug(f"Файл {file_name} записан в {file_path}")

        return file_path

    @classmethod
    def get_file_path(cls, file_name: str) -> str:
        """Получение пути до файла в папке с файлами"""
        settings = get_settings()
        return os.path.join(settings.base_dir, FILES_FOLDER, file_name)

    @classmethod
    def get_no_avatar_file_path(cls) -> str:
        """Путь до файла"""
        settings = get_settings()
        return os.path.join(settings.base_dir, IMAGES_FOLDER, NO_AVATAR_FILE)

    def delete_not_used_avatar_files(self) -> None:
        """Удаление не используемых файлов аватарок"""
        logger.debug("Выполняется удаление не используемых файлов аватарок")
        not_used_avatar_files = [
            file_name for file_name in self._get_all_file_names() if file_name not in self._get_used_avatar_files()
        ]

        for file_name in not_used_avatar_files:
            logger.info(f"Удаляем не используемый файл: {file_name}")
            os.remove(self.get_file_path(file_name))

    @staticmethod
    def _get_used_avatar_files() -> list[str]:
        """Получение используемых файлов аватарок"""
        session = next(get_session())
        avatar_files = (
            session
            .query(tables.Profile.avatar_file)
            .where(tables.Profile.avatar_file is not None)
            .all()
        )

        avatar_files = [row[0] for row in avatar_files]

        return avatar_files

    def _get_all_file_names(self) -> list[str]:
        """Получение названий всех файлов из папки с файлами"""
        file_names = [
            file_name for file_name in os.listdir(FILES_FOLDER) if os.path.isfile(self.get_file_path(file_name))
        ]

        return file_names
