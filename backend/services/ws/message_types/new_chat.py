from backend import models
from backend.services.ws.constants import MessageType
from backend.services.ws.base_messages import BaseChatWSMessage


class NewChatMessage(BaseChatWSMessage):
    """Сообщение всем участникам чата о новом чате"""
    message_type = MessageType.NEW_CHAT

    def __init__(self, chat_id: str, chat_name: str, creator: str):
        self._new_chat_data = models.NewChatData(chat_id=chat_id, chat_name=chat_name, creator=creator)
        super().__init__(login="")

    def _get_data(self) -> models.NewChatData:
        return self._new_chat_data
