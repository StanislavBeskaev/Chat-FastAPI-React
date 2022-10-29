from backend import models
from backend.db.interface import DBFacadeInterface
from backend.metrics import ws as ws_metrics
from backend.services.ws.constants import MessageType
from backend.services.ws.base_messages import BaseChatWSMessage


# TODO обновить графики в Grafana
class DeleteChatMessage(BaseChatWSMessage):
    """Сообщение об удалении чата"""

    message_type = MessageType.DELETE_CHAT
    out_metrics_counter = ws_metrics.DELETE_CHAT_OUT_WS_MESSAGE_COUNTER

    def __init__(self, login: str, chat_id: str, chat_name: str, db_facade: DBFacadeInterface):
        self._delete_chat_data = models.DeleteChat(login=login, chat_id=chat_id, chat_name=chat_name)
        super().__init__(login=login, db_facade=db_facade)

    def _get_data(self) -> models.DeleteChat:
        return self._delete_chat_data
