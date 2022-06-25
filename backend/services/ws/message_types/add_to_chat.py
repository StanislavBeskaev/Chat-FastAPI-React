from loguru import logger

from backend import models
from backend.services.ws.base_messages import BaseWSMessage
from backend.services.ws.constants import MessageType
from backend.services.ws_connection_manager import WSConnectionManager


class AddToChatMessage(BaseWSMessage):
    """Сообщение о добавлении в чат"""
    message_type = MessageType.ADD_TO_CHAT

    # TODO базовый класс для отправки сообщения одному пользователю
    def __init__(self, chat_id: str, chat_name: str, login: str):
        self._add_to_chat_data = models.AddToChatData(chat_id=chat_id, chat_name=chat_name)
        super().__init__(login=login)

    def _get_data(self) -> models.AddToChatData:
        return self._add_to_chat_data

    async def send_all(self) -> None:
        manager = WSConnectionManager()
        logger.debug(f"Отправка пользователю {self._login} сообщения : {self._content}")

        await manager.send_message_to_logins(logins=[self._login], message=self._get_message())
