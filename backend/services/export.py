from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import PosixPath
from typing import Any, Callable

from fastapi import Depends
from loguru import logger
from sqlalchemy.orm import Session

from backend.db_config import get_session
from backend.dao.chats import ChatsDAO
from backend.dao.chat_members import ChatMembersDAO
from backend.dao.contacts import ContactsDAO
from backend.dao.messages import MessagesDAO
from backend.dao.tokens import TokensDAO
from backend.dao.users import UsersDAO
from backend.services import BaseService
from backend.settings import Settings, get_settings


# TODO вынести в одно место работу с файлами и папками
TMP_FOLDER = "tmp"


# TODO название
@dataclass
class ExportSource:
    method: Callable
    file_name: str


def convert_datetime_to_timestamp(obj: Any):
    """Преобразователь для преобразования datetime к timestamp"""
    if isinstance(obj, datetime):
        return obj.timestamp()
    return obj


# TODO подумать, как назвать файл. Возможно надо назвать файл data или db_data
class ExportService(BaseService):
    """Сервис для выгрузки данных из базы данных"""

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

    def _get_tmp_folder_path(self) -> str | PosixPath:
        return os.path.join(self._settings.base_dir, TMP_FOLDER)

    def _create_tmp_folder(self) -> None:
        tmp_folder = self._get_tmp_folder_path()
        if not os.path.exists(tmp_folder):
            logger.info(f"Создана папка под временные файлы {tmp_folder}")
            os.mkdir(tmp_folder)

    def export_db_data(self):
        self._create_tmp_folder()
        # TODO нужно одинаковое название файлов для экспорта и для импорта
        export_sources = [
            ExportSource(method=self._chats_dao.get_all_chats, file_name="chats.json"),
            ExportSource(method=self._chat_members_dao.get_all_chat_members, file_name="chat_members.json"),
            ExportSource(method=self._contacts_dao.get_all_contacts, file_name="contacts.json"),
            ExportSource(method=self._messages_dao.get_all_messages, file_name="messages.json"),
            ExportSource(method=self._messages_dao.get_all_read_status_messages, file_name="messages_read_status.json"),
            ExportSource(method=self._tokens_dao.get_all_refresh_tokens, file_name="refresh_tokens.json"),
            ExportSource(method=self._users_dao.get_all_users, file_name="users.json"),
            ExportSource(method=self._users_dao.get_all_profiles, file_name="profiles.json"),
        ]

        for export_source in export_sources:
            export_file_path = os.path.join(self._get_tmp_folder_path(), export_source.file_name)
            with open(export_file_path, mode="w") as file:
                data = [item.dict() for item in export_source.method()]
                json.dump(obj=data, fp=file, indent=2, ensure_ascii=False, default=convert_datetime_to_timestamp)
                logger.info(f"Записаны данные выгрузки в файл {export_file_path}")
