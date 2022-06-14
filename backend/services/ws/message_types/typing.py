from pydantic import BaseModel, Field

from ..constants import MessageType
from ..time import get_formatted_time
from ..base_message import WSMessageData, BaseWSMessage


class InTypingMessageData(BaseModel):
    """Данные входящего сообщения о начале печатания"""
    chat_id: str = Field(alias="chatId")


class TypingMessageData(WSMessageData):
    """Данные сообщения о печатании"""
    chat_id: str


class StartTypingMessage(BaseWSMessage):
    """Сообщение о начале печатания"""
    message_type = MessageType.START_TYPING

    def __init__(self, login: str, **kwargs):
        in_typing_message_data: InTypingMessageData = InTypingMessageData.parse_obj(kwargs)
        self._chat_id = in_typing_message_data.chat_id

        super().__init__(login=login)

    def _get_data(self) -> TypingMessageData:
        return TypingMessageData(
            login=self._login,
            text="",
            time=get_formatted_time(),
            chat_id=self._chat_id
        )
