from backend import models
from backend.core.time import get_formatted_time
from backend.services.ws.base_messages import BaseChatWSMessage
from backend.services.ws.constants import MessageType


class StartTypingMessage(BaseChatWSMessage):
    """Сообщение о начале печатания"""
    message_type = MessageType.START_TYPING

    def __init__(self, login: str, **kwargs):
        in_typing_message_data: models.InTypingMessageData = models.InTypingMessageData.parse_obj(kwargs)
        self._chat_id = in_typing_message_data.chat_id

        super().__init__(login=login)

    def _get_data(self) -> models.TypingMessageData:
        return models.TypingMessageData(
            login=self._login,
            text="",
            time=get_formatted_time(),
            chat_id=self._chat_id
        )


class StopTypingMessage(StartTypingMessage):
    """Сообщение об окончании печатании"""
    message_type = MessageType.STOP_TYPING
