from backend import models
from backend.db.interface import DBFacadeInterface
from backend.metrics import ws as ws_metrics
from backend.services.ws.constants import MessageType
from backend.services.ws.base_messages import BaseChatWSMessage


class NewChatMessage(BaseChatWSMessage):
    """Сообщение всем участникам чата о новом чате"""

    message_type = MessageType.NEW_CHAT
    out_metrics_counter = ws_metrics.NEW_CHAT_OUT_WS_MESSAGE_COUNTER

    def __init__(self, chat_id: str, chat_name: str, creator: str, db_facade: DBFacadeInterface):
        self._new_chat_data = models.NewChatData(chat_id=chat_id, chat_name=chat_name, creator=creator)
        super().__init__(login="", db_facade=db_facade)

    def _get_data(self) -> models.NewChatData:
        return self._new_chat_data
