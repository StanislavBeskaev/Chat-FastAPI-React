from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
import json
import pytz
import random
from uuid import uuid4

from fastapi import WebSocket
from loguru import logger
from pydantic import BaseModel, validator, Field

from .. import tables
from ..database import get_session
from ..settings import get_settings
from .auth import AuthService
from .user import UserService


MESSAGE_TYPE_KEY = "type"
MESSAGE_DATA_KEY = "data"


class MessageType(str, Enum):
    """Типы сообщений"""
    TEXT = "TEXT"
    STATUS = "STATUS"
    START_TYPING = "START_TYPING"


class OnlineStatus(str, Enum):
    """Статусы пользователя в сети"""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class WSConnectionManager:
    """Singleton для обслуживания websocket соединений"""
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            logger.info(f"Создан instance {cls.__name__}")
            cls.__instance = super().__new__(cls)
        else:
            logger.debug(f"Взят текущий экземпляр {cls.__name__}")

        return cls.__instance

    def __init__(self):
        if not hasattr(self, "active_connections"):
            self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.debug(f"{self.__class__.__name__} новое ws соединение,"
                     f" в списке уже {len(self.active_connections)} соединений")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_personal_message(message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        logger.debug(f"{self.__class__.__name__} broadcast на {len(self.active_connections)} соединений")
        for connection in self.active_connections:
            await connection.send_text(message)


def get_current_time() -> datetime:
    settings = get_settings()
    return datetime.now(pytz.timezone(settings.timezone))


def get_formatted_time(value: datetime) -> str:
    return value.strftime("%d.%m.%y %H:%M")  # TODO подумать над отображением даты


class WSMessageData(BaseModel):
    """Данные WS сообщения"""
    login: str
    text: str | None
    time: str | datetime | None

    @validator("time")
    def convert_from_datetime(cls, value):
        if isinstance(value, datetime):
            return get_formatted_time(value)

        return value


class TextMessageData(WSMessageData):
    """Данные текстового сообщения"""
    message_id: str
    chat_id: str
    avatar_file: str | None  # TODO подумать как доставлять файл аватара на frontend


class TypingMessageData(WSMessageData):
    """Данные сообщения о печатании"""
    chat_id: str


class StatusMessageData(WSMessageData):
    """Данные статусного сообщения"""
    online_status: OnlineStatus


class WSMessage(ABC):
    """Базовый класс для работы с сообщением WS"""
    message_type = None

    def __init__(self, login: str, **kwargs):
        self._login = login
        self._content = {
            "type": self.message_type,
            "data": self._get_data().dict()
        }

    @classmethod
    def create_message_by_type(cls, message_type: MessageType, login: str, in_data: dict) -> 'WSMessage':
        type_class_mapping = {
            MessageType.TEXT: TextMessage,
            MessageType.START_TYPING: StartTypingMessage
        }

        message_class = type_class_mapping.get(message_type)

        if not message_class:
            raise ValueError(f"Неизвестный тип сообщения: {message_type}")

        return message_class(login=login, **in_data)

    # TODO позже принимать id чата, куда посылать сообщение
    async def send_all(self) -> None:
        manager = WSConnectionManager()
        logger.debug(f"Отправка сообщения: {self._content}")

        await manager.broadcast(json.dumps(self._content))

    @abstractmethod
    def _get_data(self) -> WSMessageData:
        pass


class InTypingMessageData(BaseModel):
    """Данные входящего сообщения о начале печатания"""
    chat_id: str = Field(alias="chatId")


class InTextMessageData(InTypingMessageData):
    """Данные входящего текстового сообщения"""
    text: str | None


class StartTypingMessage(WSMessage):
    """Сообщение о начале печатания"""
    message_type = MessageType.START_TYPING

    def __init__(self, login: str, **kwargs):
        in_typing_message_data: InTypingMessageData = InTextMessageData.parse_obj(kwargs)
        self._chat_id = in_typing_message_data.chat_id

        super().__init__(login=login)

    def _get_data(self) -> TypingMessageData:
        return TypingMessageData(
            login=self._login,
            text="",
            time=get_formatted_time(get_current_time()),
            chat_id=self._chat_id
        )


class TextMessage(WSMessage):
    """Текстовое сообщение"""
    message_type = MessageType.TEXT

    def __init__(self, login: str, **kwargs):
        self._session = next(get_session())

        in_text_message_data: InTextMessageData = InTextMessageData.parse_obj(kwargs)
        self._text = in_text_message_data.text
        self._chat_id = in_text_message_data.chat_id

        super().__init__(login=login)

    def _get_data(self) -> TextMessageData:
        db_message = self._create_db_message()

        user_service = UserService(session=self._session)
        data = TextMessageData(
            message_id=db_message.id,
            type=self.message_type,
            login=self._login,
            time=get_formatted_time(db_message.time),
            text=self._text,
            chat_id=self._chat_id,
            avatar_file=user_service.get_avatar_by_login(self._login)
        )

        logger.info(f"В базу сохранено текстовое сообщение: {data} ")
        return data

    def _create_db_message(self) -> tables.Message:
        auth_service = AuthService(session=self._session)
        message = tables.Message(
            id=str(uuid4()),
            text=self._text,
            user_id=auth_service.find_user_by_login(login=self._login).id,
            time=get_current_time(),
            chat_id=self._chat_id,
        )

        self._session.add(message)
        self._session.commit()
        self._session.refresh(message)

        return message


class StatusMessage(WSMessage, ABC):
    """Базовый класс статусного сообщения"""
    message_type = MessageType.STATUS
    online_status = None

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
