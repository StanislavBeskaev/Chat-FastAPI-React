from backend import models
from backend.db.interface import DBFacadeInterface
from backend.metrics import ws as ws_metrics
from backend.services.ws.base_messages import BaseChatWSMessage
from backend.services.ws.constants import MessageType


class InfoMessage(BaseChatWSMessage):
    """Информационное сообщение всем участникам чата"""
    message_type = MessageType.TEXT
    out_metrics_counter = ws_metrics.INFO_OUT_WS_MESSAGE_COUNTER

    def __init__(self, login: str, info_message: models.Message, db_facade: DBFacadeInterface):
        self._info_message = info_message
        super().__init__(login=login, db_facade=db_facade)

    def _get_data(self) -> models.InfoMessageData:
        return models.InfoMessageData(
            message_id=self._info_message.id,
            chat_id=self._info_message.chat_id,
            text=self._info_message.text,
            login=self._login,
            time=self._info_message.time
        )
