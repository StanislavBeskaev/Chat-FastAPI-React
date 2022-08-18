from backend import models
from backend.services.ws.constants import MessageType
from backend.services.ws.base_messages import BaseChatWSMessage


class ChangeMessageTextMessage(BaseChatWSMessage):
    """Сообщение всем участникам чата об изменении текста в сообщении"""
    message_type = MessageType.CHANGE_MESSAGE_TEXT

    def __init__(self, chat_id: str, message_id: str, message_text: str, change_time: str):
        self._change_message_text_data = models.ChangeMessageTextData(
            text=message_text,
            chat_id=chat_id,
            message_id=message_id,
            change_time=change_time
        )
        super().__init__(login="")

    def _get_data(self) -> models.ChangeMessageTextData:
        return self._change_message_text_data
