import json
from abc import ABC, abstractmethod

from loguru import logger

from backend import models
from backend.db.interface import DBFacadeInterface
from backend.services.ws_connection_manager import WSConnectionManager


class WSMessageInterface(ABC):
    """Интерфейс ws сообщения"""

    @abstractmethod
    async def send_all(self) -> None:
        """Отправка ws сообщения необходимым адресатам"""
        pass


class InWSMessageMixin(ABC):
    """Mixin для метрики входящих ws сообщений"""

    in_metrics_counter = None

    def __init__(self, *args, **kwargs):
        self.in_metrics_counter.inc()
        super().__init__(*args, **kwargs)


class BaseOutWSMessage(WSMessageInterface, ABC):
    """Базовый класс для работы с исходящим сообщением WS"""

    message_type = None
    out_metrics_counter = None

    def __init__(self, login: str, db_facade: DBFacadeInterface):
        self._login = login
        self._db_facade = db_facade
        self._data = self._get_data()
        self._content = {"type": self.message_type, "data": self._data.dict()}

    async def send_all(self) -> None:
        """Отправка сообщения всем подключённым пользователям"""
        manager = WSConnectionManager()
        logger.debug(f"Отправка сообщения: {self._content}")

        await manager.broadcast(message=self._get_message(), out_metrics_counter=self.out_metrics_counter)

    @abstractmethod
    def _get_data(self) -> models.WSMessageData:
        pass

    def _get_message(self) -> str:
        return json.dumps(self._content)


class BaseChatWSMessage(BaseOutWSMessage, ABC):
    """Базовый класс для работы с сообщениями в привязке к чатам"""

    async def send_all(self) -> None:
        """Отправка сообщения всем участникам чата"""
        chat_members = self._db_facade.get_chat_members(chat_id=self._data.chat_id)  # noqa
        logins_to_send = [member.login for member in chat_members]
        manager = WSConnectionManager()
        logger.debug(f"Отправка сообщения: {self._content}")

        await manager.send_message_to_logins(
            logins=logins_to_send, message=self._get_message(), out_metrics_counter=self.out_metrics_counter
        )

    @abstractmethod
    def _get_data(self) -> models.ChatMessageData:
        pass


class NoAnswerWSMessage(WSMessageInterface, ABC):
    """Базовый класс ws сообщения без ответа"""

    def __init__(self, login: str, *args, **kwargs):
        self._login = login

    async def send_all(self) -> None:
        pass


class BaseSingleUserWSMessage(BaseOutWSMessage, ABC):
    """Базовый класс исходящего сообщения конкретному пользователю"""

    async def send_all(self) -> None:
        """Отправка сообщения конкретному пользователю"""
        manager = WSConnectionManager()
        logger.debug(f"Отправка сообщения: {self._content}")
        await manager.send_message_to_logins(
            logins=[self._login], message=self._get_message(), out_metrics_counter=self.out_metrics_counter
        )

    @abstractmethod
    def _get_data(self) -> models.ChatMessageData:
        pass
