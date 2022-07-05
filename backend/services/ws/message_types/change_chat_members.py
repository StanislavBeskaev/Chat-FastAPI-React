from backend import models
from backend.services.ws.base_messages import BaseChatWSMessage
from backend.services.ws.constants import MessageType


class AddLoginToChatMessage(BaseChatWSMessage):
    """Сообщение всем участникам чата об добавлении пользователя к чату"""
    message_type = MessageType.ADD_TO_CHAT

    def __init__(self, login: str, chat_id: str, chat_name: str):
        self._chat_id = chat_id
        self._chat_name = chat_name
        super().__init__(login=login)

    def _get_data(self) -> models.ChangeChatMembersData:
        return models.ChangeChatMembersData(
            login=self._login,
            chat_id=self._chat_id,
            chat_name=self._chat_name
        )


class DeleteLoginFromChatMessage(BaseChatWSMessage):
    """Сообщение всем участникам чата об удалении пользователя из чата"""
    message_type = MessageType.DELETE_FROM_CHAT

    def __init__(self, login: str, chat_id: str, chat_name: str):
        self._chat_id = chat_id
        self._chat_name = chat_name
        super().__init__(login=login)

    def _get_data(self) -> models.ChangeChatMembersData:
        return models.ChangeChatMembersData(
            login=self._login,
            chat_id=self._chat_id,
            chat_name=self._chat_name
        )