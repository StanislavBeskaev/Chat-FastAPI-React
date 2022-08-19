from abc import ABC, abstractmethod
import json

from loguru import logger

from backend import models
from backend.dao.chat_members import ChatMembersDAO
from backend.metrics import OutWSCounter
from backend.services.ws_connection_manager import WSConnectionManager


class WSMessageInterface(ABC):
    """Интерфейс ws сообщения"""

    @abstractmethod
    async def send_all(self) -> None:
        """Отправка ws сообщения необходимым адресатам"""
        pass


class BaseWSMessage(WSMessageInterface, ABC):
    """Базовый класс для работы с сообщением WS"""
    message_type = None
    metrics_counter = OutWSCounter("ws_out", "Исходящее ws сообщение")

    def __init__(self, login: str):
        self._login = login
        self._data = self._get_data()
        self._content = {
            "type": self.message_type,
            "data": self._data.dict()
        }

    async def send_all(self) -> None:
        """Отправка сообщения всем подключённым пользователям"""
        manager = WSConnectionManager()
        logger.debug(f"Отправка сообщения: {self._content}")

        await manager.broadcast(message=self._get_message(), metrics_counter=self.metrics_counter)

    @abstractmethod
    def _get_data(self) -> models.WSMessageData:
        pass

    def _get_message(self) -> str:
        return json.dumps(self._content)


class BaseChatWSMessage(BaseWSMessage, ABC):
    """Базовый класс для работы с сообщениями в привязке к чатам"""

    async def send_all(self) -> None:
        """Отправка сообщения всем участникам чата"""
        chat_members_dao = ChatMembersDAO.create()
        chat_members = chat_members_dao.get_chat_members(chat_id=self._data.chat_id)  # noqa
        logins_to_send = [member.login for member in chat_members]
        manager = WSConnectionManager()
        logger.debug(f"Отправка сообщения: {self._content}")

        await manager.send_message_to_logins(
            logins=logins_to_send,
            message=self._get_message(),
            metrics_counter=self.metrics_counter
        )

    @abstractmethod
    def _get_data(self) -> models.ChatMessageData:
        pass


class NoAnswerWSMessage(WSMessageInterface, ABC):
    """Базовый класс ws сообщения без ответа"""

    def __init__(self, login: str):
        self._login = login

    async def send_all(self) -> None:
        pass
