from backend import models
from backend.core.time import get_formatted_time
from backend.db.interface import DBFacadeInterface
from backend.metrics import ws as ws_metrics
from backend.services.ws.base_messages import BaseChatWSMessage, InWSMessageMixin
from backend.services.ws.constants import MessageType


class TextMessage(InWSMessageMixin, BaseChatWSMessage):
    """Текстовое сообщение всем участникам чата"""

    message_type = MessageType.TEXT
    in_metrics_counter = ws_metrics.TEXT_IN_WS_MESSAGE_COUNTER
    out_metrics_counter = ws_metrics.TEXT_OUT_WS_MESSAGE_COUNTER

    def __init__(self, login: str, db_facade: DBFacadeInterface, **kwargs):
        in_text_message_data: models.InTextMessageData = models.InTextMessageData.parse_obj(kwargs)
        self._text = in_text_message_data.text
        self._chat_id = in_text_message_data.chat_id

        super().__init__(login=login, db_facade=db_facade)

    def _get_data(self) -> models.TextMessageData:
        message = self._create_db_message()

        data = models.TextMessageData(
            message_id=message.id,
            type=self.message_type,
            login=self._login,
            time=get_formatted_time(message.time),
            text=self._text,
            chat_id=self._chat_id,
        )

        return data

    def _create_db_message(self) -> models.Message:
        """Создание сообщения в базе"""
        message = self._db_facade.create_text_message(
            text=self._text, user_id=self._db_facade.find_user_by_login(login=self._login).id, chat_id=self._chat_id
        )
        self._db_facade.create_unread_messages(
            message=message, chat_members=self._db_facade.get_chat_members(chat_id=self._chat_id)
        )

        return message
