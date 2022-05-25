import random
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

from loguru import logger
from pydantic import BaseModel

from .user import UserService
from .ws import WSConnectionManager


class MessageType(str, Enum):
    """Типы сообщений"""
    TEXT = "TEXT"
    STATUS = "STATUS"


def get_current_time() -> str:
    now = datetime.now()
    current_time = now.strftime("%H:%M")

    return current_time


class MessageData(BaseModel):
    """Данные сообщения"""
    type: MessageType
    time: str = get_current_time()
    login: str
    text: str | None
    avatar_file: str | None


class BaseMessage(ABC):
    """Базовый класс для работы с сообщением WS"""
    message_type = None

    def __init__(self, login: str, user_service: UserService, text: str = "", ):
        self._login = login
        self._text = text
        self._data = MessageData(login=login, text=text, type=self.message_type)
        self._user_service = user_service

        self._set_avatar_file()

    # TODO позже принимать id чата куда посылать сообщение
    async def send_all(self) -> None:
        manager = WSConnectionManager()
        logger.debug(f"Отправка сообщения: {self._data}")

        await manager.broadcast(self._data.json())

    def _set_avatar_file(self) -> None:
        self._data.avatar_file = self._user_service.get_avatar_by_login(login=self._login)


class TextMessage(BaseMessage):
    """Текстовое сообщение"""
    message_type = MessageType.TEXT


class StatusMessage(BaseMessage, ABC):
    """Базовый класс статусного сообщения"""
    message_type = MessageType.STATUS

    def __init__(self, login: str, user_service: UserService):
        super().__init__(login=login, user_service=user_service)
        self._data.type = MessageType.STATUS
        self._data.text = self._get_message_text()

    def _get_message_text(self) -> str:
        return random.choice(self._get_text_templates()).format(login=self._login)

    @abstractmethod
    def _get_text_templates(self) -> list[str]:
        pass


class OnlineMessage(StatusMessage):
    """Сообщение при подключении пользователя"""
    def _get_text_templates(self) -> list[str]:
        # TODO добавить больше фраз
        online_text_templates = [
            "Пользователь {login} в сети",
            "К нам подкрался {login}",
            "{login} внезапно тут",
            "Пользователь {login} уже онлайн"
        ]

        return online_text_templates


class OfflineMessage(StatusMessage):
    """Сообщение об отключении пользователя"""
    def _get_text_templates(self) -> list[str]:
        # TODO добавить больше фраз
        offline_text_templates = [
            "{login} вышел",
            "Куда ты {login}?",
            "{login} offline",
            "Пользователь {login} решил смыться"
        ]

        return offline_text_templates
