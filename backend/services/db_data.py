from dataclasses import dataclass
from datetime import datetime
import json
import io
import os
from pathlib import PosixPath
from typing import Any, Callable
from zipfile import ZipFile

from fastapi import Depends, UploadFile
from loguru import logger
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend import tables
from backend.db_config import get_session
from backend.dao.chats import ChatsDAO
from backend.dao.chat_members import ChatMembersDAO
from backend.dao.contacts import ContactsDAO
from backend.dao.messages import MessagesDAO
from backend.dao.tokens import TokensDAO
from backend.dao.users import UsersDAO
from backend.services import BaseService
from backend.settings import Settings, get_settings
from backend.tables import Base


TMP_FOLDER = "tmp"
EXPORT_FOLDER = "export"
IMPORT_FOLDER = "import"


@dataclass
class DBDataSource:
    export_method: Callable
    file_name: str
    delete_priority: int
    insert_priority: int
    table: Base


def convert_datetime_to_timestamp(obj: Any):
    """Преобразования datetime к timestamp"""
    if isinstance(obj, datetime):
        return obj.timestamp()
    return obj


def convert_timestamp_str_to_datetime(timestamp_str: str) -> datetime:
    """Преобразование строчного представления timestamp в datetime"""
    return datetime.fromtimestamp(float(timestamp_str))


class DBDataService(BaseService):
    """Сервис для выгрузки и загрузки данных базы"""

    def __init__(self, session: Session = Depends(get_session), settings: Settings = Depends(get_settings)):
        super().__init__(session=session)
        self._settings = settings
        # TODO тут бы пригодился DBFacade
        self._chats_dao = ChatsDAO(session=session)
        self._chat_members_dao = ChatMembersDAO(session=session)
        self._contacts_dao = ContactsDAO(session=session)
        self._messages_dao = MessagesDAO(session=session)
        self._tokens_dao = TokensDAO(session=session)
        self._users_dao = UsersDAO(session=session)
        self._db_data_sources = [
            DBDataSource(export_method=self._users_dao.get_all_users, file_name="users.json",
                         delete_priority=8, insert_priority=1, table=tables.User),
            DBDataSource(export_method=self._chats_dao.get_all_chats, file_name="chats.json",
                         delete_priority=6, insert_priority=2, table=tables.Chat),
            DBDataSource(export_method=self._messages_dao.get_all_messages, file_name="messages.json",
                         delete_priority=5, insert_priority=3, table=tables.Message),
            DBDataSource(export_method=self._contacts_dao.get_all_contacts, file_name="contacts.json",
                         delete_priority=4, insert_priority=4, table=tables.Contact),
            DBDataSource(export_method=self._chat_members_dao.get_all_chat_members, file_name="chat_members.json",
                         delete_priority=3, insert_priority=5, table=tables.ChatMember),
            DBDataSource(export_method=self._messages_dao.get_all_read_status_messages, file_name="messages_read_status.json",  # noqa
                         delete_priority=2, insert_priority=6, table=tables.MessageReadStatus),
            DBDataSource(export_method=self._tokens_dao.get_all_refresh_tokens, file_name="refresh_tokens.json",
                         delete_priority=2, insert_priority=7, table=tables.RefreshToken),
            DBDataSource(export_method=self._users_dao.get_all_profiles, file_name="profiles.json",
                         delete_priority=1, insert_priority=8, table=tables.Profile),
        ]

    def export_db_data(self) -> io.BytesIO:
        """
        Выгрузка данных из базы в виде zip файла.
        Формирует json файлы с данными всех таблиц и записывает в zip файл.
        """
        self._create_export_folder()
        return self._make_export_zip_object()

    def import_db_data(self, import_zip_file: UploadFile) -> None:
        """Импорт данных в базу из zip файла"""
        self._unzip_import_zip_file(
            import_zip_file_path=self._save_import_zip_file(import_zip_file=import_zip_file)
        )
        self._clear_tables()
        self._insert_import_db_data()
        # Если поменяется набор таблиц, наименования таблиц или последовательностей, то адаптировать
        self._set_correct_table_sequences_value()

    def _create_export_folder(self) -> None:
        export_folder_path = self._get_export_folder_path()
        self._create_folder(export_folder_path)

    def _create_import_folder(self) -> None:
        import_folder_path = self._get_import_folder_path()
        self._create_folder(import_folder_path)

    def _get_export_folder_path(self) -> str | PosixPath:
        return self._get_folder_path_in_tmp_folder(folder_name=EXPORT_FOLDER)

    def _get_import_folder_path(self) -> str | PosixPath:
        return self._get_folder_path_in_tmp_folder(folder_name=IMPORT_FOLDER)

    def _get_folder_path_in_tmp_folder(self, folder_name: str) -> str | PosixPath:
        return os.path.join(self._settings.base_dir, TMP_FOLDER, folder_name)

    def _make_export_zip_object(self):
        export_object = io.BytesIO()
        with ZipFile(export_object, "w") as zip_file:
            for export_source in self._db_data_sources:
                export_source_file_path = self._export_db_data_source(db_data_source=export_source)
                zip_file.write(filename=export_source_file_path, arcname=os.path.basename(export_source_file_path))
                logger.info(f"Файл {export_source_file_path} записан в выгружаемый архив")

        export_object.seek(0)
        return export_object

    @staticmethod
    def _create_folder(folder_path: str) -> None:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            logger.info(f"Создана папка под временные файлы {folder_path}")

    def _export_db_data_source(self, db_data_source: DBDataSource) -> str | PosixPath:
        export_folder_path = self._get_export_folder_path()
        export_file_path = os.path.join(export_folder_path, db_data_source.file_name)

        with open(export_file_path, mode="w") as file:
            export_data = [item.dict() for item in db_data_source.export_method()]
            json.dump(obj=export_data, fp=file, indent=2, ensure_ascii=False, default=convert_datetime_to_timestamp)
            logger.info(f"Записаны данные выгрузки в файл {export_file_path}")

        return export_file_path

    def _save_import_zip_file(self, import_zip_file: UploadFile) -> str | PosixPath:
        self._create_import_folder()
        import_zip_file_path = os.path.join(self._get_import_folder_path(), "import.zip")

        with open(import_zip_file_path, mode="wb") as import_file:
            import_file.write(import_zip_file.file.read())
        logger.info(f"Входной zip архив записан в файл {import_zip_file_path}")
        return import_zip_file_path

    def _unzip_import_zip_file(self, import_zip_file_path) -> None:
        logger.debug(f"start unzip {import_zip_file_path}")
        with ZipFile(import_zip_file_path, mode="r") as zip_file:
            zip_file.extractall(path=self._get_import_folder_path())
        logger.debug(f"finish unzip {import_zip_file_path}")

    def _clear_tables(self) -> None:
        db_data_sources_delete_order = sorted(
            self._db_data_sources,
            key=lambda x: x.delete_priority
        )
        for db_data_source in db_data_sources_delete_order:
            self.session.query(db_data_source.table).delete()
            logger.info(f"Очищаем таблицу {db_data_source.table.__tablename__}")
        self.session.commit()
        logger.info("Все таблицы очищены")

    def _insert_import_db_data(self) -> None:
        db_data_sources_insert_order = sorted(
            self._db_data_sources,
            key=lambda x: x.insert_priority
        )

        for db_data_source in db_data_sources_insert_order:
            self._insert_import_data_to_table(
                import_data=self._read_import_data_file(db_data_source.file_name),
                table=db_data_source.table
            )

        self.session.commit()
        logger.info("commit вставки импортированных данных")

    def _read_import_data_file(self, file_name: str) -> list[dict]:
        import_data_file_path = os.path.join(self._get_import_folder_path(), file_name)
        with open(import_data_file_path, mode="r") as import_file:
            import_data = json.load(import_file, parse_float=convert_timestamp_str_to_datetime)
            logger.info(f"Прочитан файл {import_data_file_path}")
            return import_data

    def _insert_import_data_to_table(self, import_data: list[dict], table: Base) -> None:
        table_objects = [table(**data) for data in import_data]
        self.session.bulk_save_objects(table_objects)
        logger.info(f"Вставлены данные в таблицу {table.__tablename__}")

    def _set_correct_table_sequences_value(self) -> None:
        table_sequences_to_restart = (
            ("messages_read_status_id_seq", tables.MessageReadStatus),
            ("chat_members_id_seq", tables.ChatMember),
            ("contacts_id_seq", tables.Contact),
            ("profiles_id_seq", tables.Profile),
            ("refresh_tokens_id_seq", tables.RefreshToken),
            ("users_id_seq", tables.User),
        )

        for sequence_name, table in table_sequences_to_restart:
            next_table_id = self.session.query(func.max(table.id)).scalar() + 1
            self.session.execute(
                f"ALTER SEQUENCE {sequence_name} RESTART WITH {next_table_id}"
            )
            logger.info(f"Для последовательности {sequence_name} выставлено значение {next_table_id}")
        self.session.commit()
        logger.info("Для всех последовательностей установлены корректные значения")
