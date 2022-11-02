import os

from fastapi import UploadFile
from loguru import logger

from backend.services import BaseService
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


class FilesService(BaseService):
    """Сервис для управления файлами"""

    @classmethod
    def get_file_extension(cls, file_name) -> str:
        """Получение расширения файла"""
        filename, file_extension = os.path.splitext(file_name)

        return file_extension

    @classmethod
    def get_file_path(cls, file_name: str) -> str:
        """Получение пути до файла в папке с файлами"""
        return os.path.join(cls._get_files_folder_path(), file_name)

    @classmethod
    def get_no_avatar_file_path(cls) -> str:
        """Путь до файла"""
        settings = get_settings()
        return os.path.join(settings.base_dir, IMAGES_FOLDER, NO_AVATAR_FILE)

    @classmethod
    def replace_files_by_folder(cls, folder_path: str) -> None:
        """Замена папки с файлами на указанную папку"""
        logger.info(f"Заменяем папку с файлами на папку: {folder_path}")
        files_folder_path = cls._get_files_folder_path()
        if os.listdir(files_folder_path):
            logger.debug(f"Папка с файлами не пустая, очищаем")
            cls.clear_files_folder()

        os.rename(src=folder_path, dst=files_folder_path)
        logger.info(f"Содержимое папки с файлами заменено")

    @classmethod
    def clear_files_folder(cls) -> None:
        """Очистка папки с файлами"""
        logger.info("Очищаем папку с файлами")
        files_folder_path = cls._get_files_folder_path()
        for file_name in os.listdir(files_folder_path):
            os.remove(cls.get_file_path(file_name))
            logger.debug(f"Удалён файл {file_name}")
        logger.info(f"Очищена папка с файлами")

    @check_files_folder
    def save_file(self, file: UploadFile, file_name: str) -> str:
        """Сохранение файла"""
        file_path = self.get_file_path(file_name)
        with open(file_path, mode="wb") as writable_file:
            writable_file.write(file.file.read())

        logger.debug(f"Файл {file_name} записан в {file_path}")

        return file_path

    def delete_not_used_avatar_files(self) -> None:
        """Удаление не используемых файлов аватарок"""
        logger.debug("Выполняется удаление не используемых файлов аватарок")
        not_used_avatar_files = [
            file_name
            for file_name in self.get_all_file_names()
            if file_name not in self._db_facade.get_used_avatar_files()
        ]

        for file_name in not_used_avatar_files:
            logger.info(f"Удаляем не используемый файл: {file_name}")
            os.remove(self.get_file_path(file_name))

    def get_all_file_names(self) -> list[str]:
        """Получение названий всех файлов из папки с файлами"""
        file_names = [
            file_name for file_name in os.listdir(FILES_FOLDER) if os.path.isfile(self.get_file_path(file_name))
        ]

        return file_names

    @staticmethod
    def _get_files_folder_path() -> str:
        return os.path.join(get_settings().base_dir, FILES_FOLDER)
