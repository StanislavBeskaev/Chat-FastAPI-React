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


class OnlineStatus(str, Enum):
    """Статусы пользователя в сети"""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


def get_current_time() -> str:
    now = datetime.now()
    current_time = now.strftime("%H:%M")

    return current_time


class MessageData(BaseModel):
    """Данные сообщения"""
    type: MessageType
    online_status: OnlineStatus | None = None
    time: str
    login: str
    text: str | None
    avatar_file: str | None


class BaseMessage(ABC):
    """Базовый класс для работы с сообщением WS"""
    message_type = None
    online_status = None

    def __init__(self, login: str, user_service: UserService, text: str = "", ):
        self._login = login
        self._text = text
        self._data = MessageData(
            type=self.message_type,
            online_status=self.online_status,
            time=get_current_time(),
            login=login,
            text=text,
            avatar_file=user_service.get_avatar_by_login(login=login)
        )
        self._user_service = user_service

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
    online_status = OnlineStatus.ONLINE


class StatusMessage(BaseMessage, ABC):
    """Базовый класс статусного сообщения"""
    message_type = MessageType.STATUS

    def __init__(self, login: str, user_service: UserService):
        super().__init__(login=login, user_service=user_service)
        self._data.type = MessageType.STATUS
        self._data.text = self._get_status_message_text()

    def _get_status_message_text(self) -> str:
        return random.choice(self._get_text_templates()).format(login=self._login)

    @abstractmethod
    def _get_text_templates(self) -> list[str]:
        pass


class OnlineMessage(StatusMessage):
    """Сообщение при подключении пользователя"""
    online_status = OnlineStatus.ONLINE

    def _get_text_templates(self) -> list[str]:
        # TODO добавить больше фраз
        online_text_templates = [
            "Пользователь {login} в сети",
            "К нам подкрался {login}",
            "{login} внезапно тут",
            "Пользователь {login} уже онлайн",
            "А вот и {login}",
            "Хорошо, что ты пришёл {login}",
            "Пользователь {login} ворвался в чат"
        ]

        return online_text_templates


class OfflineMessage(StatusMessage):
    """Сообщение об отключении пользователя"""
    online_status = OnlineStatus.OFFLINE

    def _get_text_templates(self) -> list[str]:
        # TODO добавить больше фраз
        offline_text_templates = [
            "{login} вышел",
            "Куда ты {login}?",
            "{login} offline",
            "Пользователь {login} решил смыться",
            "Стало пусто без {login}",
            "Пока {login}",
        ]

        return offline_text_templates
