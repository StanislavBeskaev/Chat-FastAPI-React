from abc import ABC, abstractmethod
import json

from loguru import logger

from backend import models
from backend.services.get_chat_members import get_chat_members
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

    def __init__(self, login: str):
        self._login = login
        self._data = self._get_data()
        self._content = {
            "type": self.message_type,
            "data": self._data.dict()
        }

    async def send_all(self) -> None:
        manager = WSConnectionManager()
        logger.debug(f"Отправка сообщения: {self._content}")

        await manager.broadcast(self._get_message())

    @abstractmethod
    def _get_data(self) -> models.WSMessageData:
        pass

    def _get_message(self) -> str:
        return json.dumps(self._content)


class BaseChatWSMessage(BaseWSMessage, ABC):
    """Базовый класс для работы с сообщениями в привязке к чатам"""

    async def send_all(self) -> None:
        chat_members = get_chat_members(chat_id=self._data.chat_id)  # noqa
        logins_to_send = [member.login for member in chat_members]
        manager = WSConnectionManager()
        logger.debug(f"Отправка сообщения: {self._content}")

        await manager.send_message_to_logins(logins=logins_to_send, message=self._get_message())

    @abstractmethod
    def _get_data(self) -> models.ChatMessageData:
        pass


class SingleLoginChatMessage(BaseWSMessage, ABC):
    """Базовый класс для отправки сообщения о чате одному пользователю"""

    def __init__(self, chat_id: str, chat_name: str, login: str):
        self._chat_name_data = models.ChatNameData(chat_id=chat_id, chat_name=chat_name)
        super().__init__(login=login)

    def _get_data(self) -> models.ChatNameData:
        return self._chat_name_data

    async def send_all(self) -> None:
        raise RuntimeError("send_all не применимо для сообщения конкретному пользователю")

    async def send(self) -> None:
        """Отправка сообщения пользователю"""
        manager = WSConnectionManager()
        logger.debug(f"Отправка пользователю {self._login} сообщения : {self._content}")

        await manager.send_message_to_logins(logins=[self._login], message=self._get_message())


class NoAnswerWSMessage(WSMessageInterface, ABC):
    """Базовый класс ws сообщения без ответа"""

    def __init__(self, login: str):
        self._login = login

    async def send_all(self) -> None:
        pass
