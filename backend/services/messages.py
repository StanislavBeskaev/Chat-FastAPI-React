from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime
from enum import Enum
import pytz
import random
from uuid import uuid4

from loguru import logger
from pydantic import BaseModel, validator, Field

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
    return value.strftime("%d.%m.%y %H:%M")  # TODO подумать над отображением даты


class InMessage(BaseModel):
    """Входное сообщение"""
    text: str
    chat_id: str = Field(alias="chatId")


class WSMessageData(BaseModel):
    """Данные WS сообщения"""
    type: MessageType
    login: str
    text: str | None
    time: str | datetime

    @validator("time")
    def convert_from_datetime(cls, value):
        if isinstance(value, datetime):
            return get_formatted_time(value)

        return value


class TextMessageData(WSMessageData):
    """Данные текстового сообщения"""
    id: str
    chat_id: str
    avatar_file: str | None  # TODO подумать как доставлять файл аватара на frontend


class StatusMessageData(WSMessageData):
    """Данные статусного сообщения"""
    online_status: OnlineStatus


class BaseMessage(ABC):
    """Базовый класс для работы с сообщением WS"""
    message_type = None

    def __init__(self, login: str):
        self._login = login
        self._data = self._get_data()

    # TODO позже принимать id чата, куда посылать сообщение
    async def send_all(self) -> None:
        manager = WSConnectionManager()
        logger.debug(f"Отправка сообщения: {self._data}")

        await manager.broadcast(self._data.json())

    @abstractmethod
    def _get_data(self) -> WSMessageData:
        pass


class TextMessage(BaseMessage):
    """Текстовое сообщение"""
    message_type = MessageType.TEXT

    def __init__(
            self,
            login: str,
            user_service: UserService,
            text: str = "",
            chat_id: str = get_settings().main_chat_id
    ):
        self._chat_id = chat_id
        self._user_service = user_service
        self._text = text
        super().__init__(login=login)

    def _get_data(self) -> TextMessageData:
        db_message = self._create_db_message()

        data = TextMessageData(
            id=db_message.id,
            type=self.message_type,
            login=self._login,
            time=get_formatted_time(db_message.time),
            text=self._text,
            chat_id=self._chat_id,
            avatar_file=self._user_service.get_avatar_by_login(self._login)
        )

        logger.info(f"В базу сохранено сообщение: {data} ")
        return data

    def _create_db_message(self) -> tables.Message:
        session = next(get_session())

        auth_service = AuthService(session=session)
        message = tables.Message(
            id=str(uuid4()),
            text=self._text,
            user_id=auth_service.find_user_by_login(login=self._login).id,
            time=get_current_time(),
            chat_id=self._chat_id,
        )

        session.add(message)
        session.commit()
        session.refresh(message)

        return message


class StatusMessage(BaseMessage, ABC):
    """Базовый класс статусного сообщения"""
    message_type = MessageType.STATUS
    online_status = None

    def __init__(self, login: str):
        super().__init__(login=login)

    def _get_data(self) -> StatusMessageData:
        data = StatusMessageData(
            type=self.message_type,
            login=self._login,
            text=self._get_status_message_text(),
            time=get_formatted_time(get_current_time()),
            online_status=self.online_status
        )

        return data

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
            "Пользователь {login} ворвался в чат",
            "{login} уже тут",
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

    def get_many(self) -> dict[str, list[TextMessageData]]:
        """Получение всех сообщений"""
        messages = (
            self.session
            .query(
                tables.Message.id,
                tables.Message.time,
                tables.User.login,
                tables.Message.text,
                tables.Message.chat_id,
                tables.Profile.avatar_file
            )
            .where(tables.Message.user_id == tables.User.id)
            .where(tables.Profile.user == tables.User.id)
            .order_by(tables.Message.time)
            .all()
        )

        # TODO посмотреть способ получше
        columns = ("id", "time", "login", "text", "chat_id", "avatar_file")

        messages = [TextMessageData(type=MessageType.TEXT, **dict(zip(columns, data))) for data in messages]

        return self._convert_messages_to_chats(messages=messages)

    @staticmethod
    def _convert_messages_to_chats(messages: list[TextMessageData]) -> dict[str, list[TextMessageData]]:
        chats = defaultdict(list)

        for message_data in messages:
            chats[message_data.chat_id].append(message_data)

        return chats
