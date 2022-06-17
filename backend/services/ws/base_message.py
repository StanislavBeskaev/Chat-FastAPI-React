from abc import ABC, abstractmethod
import json

from loguru import logger

from backend.models import WSMessageData
from .connection_manager import WSConnectionManager


class BaseWSMessage(ABC):
    """Базовый класс для работы с сообщением WS"""
    message_type = None

    def __init__(self, login: str):
        self._login = login
        self._content = {
            "type": self.message_type,
            "data": self._get_data().dict()
        }

    # TODO позже принимать id чата, куда посылать сообщение
    async def send_all(self) -> None:
        manager = WSConnectionManager()
        logger.debug(f"Отправка сообщения: {self._content}")

        await manager.broadcast(json.dumps(self._content))

    @abstractmethod
    def _get_data(self) -> WSMessageData:
        pass
