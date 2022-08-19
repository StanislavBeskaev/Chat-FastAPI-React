from backend import models
from backend.metrics import ws as ws_metrics
from backend.services.ws.constants import MessageType
from backend.services.ws.base_messages import BaseChatWSMessage


class ChangeChatNameMessage(BaseChatWSMessage):
    """Сообщение всем участникам чата об изменении названия чата"""
    message_type = MessageType.CHANGE_CHAT_NAME
    out_metrics_counter = ws_metrics.CHANGE_CHAT_NAME_OUT_WS_MESSAGE_COUNTER

    def __init__(self, chat_id: str, chat_name):
        self._new_chat_data = models.ChatChangeNameData(chat_id=chat_id, chat_name=chat_name)
        super().__init__(login="")

    def _get_data(self) -> models.ChatChangeNameData:
        return self._new_chat_data
