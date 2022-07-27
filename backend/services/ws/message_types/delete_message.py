from backend import models
from backend.services.ws.constants import MessageType
from backend.services.ws.base_messages import BaseChatWSMessage


class DeleteMessageMessage(BaseChatWSMessage):
    """Сообщение об удалении сообщения"""
    message_type = MessageType.DELETE_MESSAGE

    def __init__(self, chat_id: str, message_id: str):
        self._delete_message_data = models.DeleteMessageData(
            chat_id=chat_id,
            message_id=message_id
        )
        super().__init__(login="")

    def _get_data(self) -> models.DeleteMessageData:
        return self._delete_message_data
