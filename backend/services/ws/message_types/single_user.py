from backend.services.ws.base_messages import SingleLoginChatMessage
from backend.services.ws.constants import MessageType


class AddToChatMessage(SingleLoginChatMessage):
    """Сообщение о добавлении пользователя в чат в чат"""
    message_type = MessageType.ADD_TO_CHAT


class DeleteFromChatMessage(SingleLoginChatMessage):
    """Сообщение об удалении пользователя из чата"""
    message_type = MessageType.DELETE_FROM_CHAT
