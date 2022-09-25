from backend import models
from backend.db.interface import DBFacadeInterface
from backend.metrics import ws as ws_metrics
from backend.services.ws.constants import MessageType
from backend.services.ws.base_messages import BaseChatWSMessage


class ChangeMessageTextMessage(BaseChatWSMessage):
    """Сообщение всем участникам чата об изменении текста в сообщении"""
    message_type = MessageType.CHANGE_MESSAGE_TEXT
    out_metrics_counter = ws_metrics.CHANGE_MESSAGE_TEXT_OUT_WS_MESSAGE_COUNTER

    def __init__(self, chat_id: str, message_id: str, message_text: str, change_time: str, db_facade: DBFacadeInterface):
        self._change_message_text_data = models.ChangeMessageTextData(
            text=message_text,
            chat_id=chat_id,
            message_id=message_id,
            change_time=change_time
        )
        super().__init__(login="", db_facade=db_facade)

    def _get_data(self) -> models.ChangeMessageTextData:
        return self._change_message_text_data
