from backend import models
from backend.db.interface import DBFacadeInterface
from backend.metrics import ws as ws_metrics
from backend.services.ws.constants import MessageType
from backend.services.ws.base_messages import BaseChatWSMessage


class DeleteMessageMessage(BaseChatWSMessage):
    """Сообщение всем участникам чата об удалении сообщения"""
    message_type = MessageType.DELETE_MESSAGE
    out_metrics_counter = ws_metrics.DELETE_MESSAGE_OUT_WS_MESSAGE_COUNTER

    def __init__(self, chat_id: str, message_id: str, db_facade: DBFacadeInterface):
        self._delete_message_data = models.DeleteMessageData(
            chat_id=chat_id,
            message_id=message_id
        )
        super().__init__(login="", db_facade=db_facade)

    def _get_data(self) -> models.DeleteMessageData:
        return self._delete_message_data
