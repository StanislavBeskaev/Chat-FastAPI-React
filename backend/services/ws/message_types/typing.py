from backend import models
from backend.core.time import get_formatted_time
from backend.metrics import ws as ws_metrics
from backend.services.ws.base_messages import BaseChatWSMessage, InWSMessageMixin
from backend.services.ws.constants import MessageType


class StartTypingMessage(InWSMessageMixin, BaseChatWSMessage):
    """Сообщение всем участникам чата о начале печатания"""
    message_type = MessageType.START_TYPING
    in_metrics_counter = ws_metrics.START_TYPING_IN_WS_MESSAGE_CNT
    out_metrics_counter = ws_metrics.START_TYPING_OUT_WS_MESSAGE_CNT

    def __init__(self, login: str, **kwargs):
        in_typing_message_data = models.InTypingMessageData.parse_obj(kwargs)
        self._chat_id = in_typing_message_data.chat_id

        super().__init__(login=login)

    def _get_data(self) -> models.TypingMessageData:
        return models.TypingMessageData(
            login=self._login,
            text="",
            time=get_formatted_time(),
            chat_id=self._chat_id
        )


class StopTypingMessage(StartTypingMessage):
    """Сообщение всем участникам чата об окончании печатании"""
    message_type = MessageType.STOP_TYPING
    in_metrics_counter = ws_metrics.STOP_TYPING_IN_WS_MESSAGE_CNT
    out_metrics_counter = ws_metrics.STOP_TYPING_OUT_WS_MESSAGE_CNT

