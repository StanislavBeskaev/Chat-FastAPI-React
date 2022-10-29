from backend import models
from backend.db.interface import DBFacadeInterface
from backend.metrics import ws as ws_metrics
from backend.services.ws.base_messages import BaseChatWSMessage
from backend.services.ws.constants import MessageType


class AddLoginToChatMessage(BaseChatWSMessage):
    """Сообщение всем участникам чата об добавлении пользователя к чату"""

    message_type = MessageType.ADD_TO_CHAT
    out_metrics_counter = ws_metrics.ADD_CHAT_MEMBER_OUT_WS_MESSAGE_COUNTER

    def __init__(self, login: str, chat_id: str, chat_name: str, db_facade: DBFacadeInterface):
        self._chat_id = chat_id
        self._chat_name = chat_name
        super().__init__(login=login, db_facade=db_facade)

    def _get_data(self) -> models.ChangeChatMembersData:
        return models.ChangeChatMembersData(login=self._login, chat_id=self._chat_id, chat_name=self._chat_name)


class DeleteLoginFromChatMessage(BaseChatWSMessage):
    """Сообщение всем участникам чата об удалении пользователя из чата"""

    message_type = MessageType.DELETE_FROM_CHAT
    out_metrics_counter = ws_metrics.DELETE_CHAT_MEMBER_OUT_WS_MESSAGE_COUNTER

    def __init__(self, login: str, chat_id: str, chat_name: str, db_facade: DBFacadeInterface):
        self._chat_id = chat_id
        self._chat_name = chat_name
        super().__init__(login=login, db_facade=db_facade)

    def _get_data(self) -> models.ChangeChatMembersData:
        return models.ChangeChatMembersData(login=self._login, chat_id=self._chat_id, chat_name=self._chat_name)
