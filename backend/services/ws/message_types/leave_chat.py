from backend import models
from backend.db.interface import DBFacadeInterface
from backend.metrics import ws as ws_metrics
from backend.services.ws.constants import MessageType
from backend.services.ws.base_messages import BaseSingleUserWSMessage


# TODO обновить графики в Grafana
class LeaveChatMessage(BaseSingleUserWSMessage):
    """Сообщение о выходе из чата"""

    message_type = MessageType.LEAVE_CHAT
    out_metrics_counter = ws_metrics.LEAVE_CHAT_OUT_WS_MESSAGE_COUNTER

    def __init__(self, chat_id: str, chat_name: str, login: str, db_facade: DBFacadeInterface):
        self._leave_chat_data = models.LeaveChat(chat_id=chat_id, chat_name=chat_name)
        super().__init__(login=login, db_facade=db_facade)

    def _get_data(self) -> models.LeaveChat:
        return self._leave_chat_data
