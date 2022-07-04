from backend import models
from backend import tables
from backend.services.ws.base_messages import BaseChatWSMessage
from backend.services.ws.constants import MessageType


class InfoMessage(BaseChatWSMessage):
    """Информационное сообщение"""
    message_type = MessageType.TEXT

    def __init__(self, login: str, info_message: tables.Message):
        self._info_message = info_message
        super().__init__(login=login)

    def _get_data(self) -> models.InfoMessageData:
        return models.InfoMessageData(
            message_id=self._info_message.id,
            chat_id=self._info_message.chat_id,
            text=self._info_message.text,
            login=self._login,
            time=self._info_message.time
        )
