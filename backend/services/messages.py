import pytz
import random
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from uuid import uuid4

from loguru import logger
from pydantic import BaseModel, validator

from .. import tables
from ..database import get_session
from ..settings import get_settings
from . import BaseService
from .auth import AuthService
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


def get_current_time() -> datetime:
    settings = get_settings()
    return datetime.now(pytz.timezone(settings.timezone))


def get_formatted_time(value: datetime) -> str:
    return value.strftime("%H:%M")


class MessageData(BaseModel):
    """Данные сообщения"""
    id: str
    type: MessageType
    online_status: OnlineStatus | None = None
    time: str | datetime
    login: str
    text: str | None
    avatar_file: str | None

    @validator("time")
    def convert_from_datetime(cls, value):
        if isinstance(value, datetime):
            logger.warning(f"MessageData datetime: {value}")
            return get_formatted_time(value)

        return value


class BaseMessage(ABC):
    """Базовый класс для работы с сообщением WS"""
    message_type = None
    online_status = None

    def __init__(self, login: str, user_service: UserService, text: str = "", ):
        self._login = login
        self._text = text
        self._user_service = user_service

        db_message = self._create_db_message()

        self._data = MessageData(
            id=db_message.id,
            type=self.message_type,
            online_status=self.online_status,
            time=get_formatted_time(db_message.time),
            login=login,
            text=text,
            avatar_file=user_service.get_avatar_by_login(login)
        )

        logger.info(f"В базу сохранено сообщение: {self._data} ")

    # TODO позже принимать id чата, куда посылать сообщение
    async def send_all(self) -> None:
        manager = WSConnectionManager()
        logger.debug(f"Отправка сообщения: {self._data}")

        await manager.broadcast(self._data.json())

    # TODO статусные сообщения хранить в другой таблице?
    def _create_db_message(self) -> tables.Message:
        session = next(get_session())

        auth_service = AuthService(session=session)
        message = tables.Message(
            id=str(uuid4()),
            text=self._text,
            user_id=auth_service.find_user_by_login(login=self._login).id,
            time=get_current_time(),
            type=self.message_type,
            online_status=self.online_status
        )

        session.add(message)
        session.commit()
        session.refresh(message)

        return message


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


class MessageService(BaseService):
    """Сервис для работы с сообщениями"""

    def get_many(self) -> list[MessageData]:
        """Получение всех сообщений"""
        messages = (
            self.session
            .query(
                tables.Message.id,
                tables.Message.type,
                tables.Message.online_status,
                tables.Message.time,
                tables.User.login,
                tables.Message.text,
                tables.Profile.avatar_file
            )
            .where(tables.Message.user_id == tables.User.id)
            .where(tables.Profile.user == tables.User.id)
            .where(tables.Message.type == MessageType.TEXT)
            .order_by(tables.Message.time)
            .all()
        )

        # TODO посмотреть способ получше
        columns = ("id", "type", "online_status", "time", "login", "text", "avatar_file")

        return [MessageData(**dict(zip(columns, data))) for data in messages]
