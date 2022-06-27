import os
from fastapi import UploadFile
from loguru import logger


FILES_FOLDER = "files"
IMAGES_FOLDER = "images"
NO_AVATAR_FILE = "no_avatar.png"


def check_files_folder(func):
    def wrapper(*args, **kwargs):
        if not os.path.exists(FILES_FOLDER):
            logger.debug(f"Создана папка под файлы {FILES_FOLDER}")
            os.mkdir(FILES_FOLDER)

        return func(*args, **kwargs)

    return wrapper


class FilesService:
    """Сервис для управления файлами"""

    @classmethod
    def get_file_extension(cls, file_name) -> str:
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
        return os.path.join(FILES_FOLDER, file_name)

    @classmethod
    def get_no_avatar_file_path(cls) -> str:
        return os.path.join(IMAGES_FOLDER, NO_AVATAR_FILE)
