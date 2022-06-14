from .base_message import BaseWSMessage, WSMessageData
from .connection_manager import WSConnectionManager
from .constants import MESSAGE_TYPE_KEY, MESSAGE_DATA_KEY, MessageType
from .message_types import (
    OnlineMessage,
    OfflineMessage,
    StartTypingMessage,
    TextMessage,
    StopTypingMessage
)


def create_message_by_type(message_type: MessageType, login: str, in_data: dict) -> BaseWSMessage:
    type_class_mapping = {
        MessageType.TEXT: TextMessage,
        MessageType.START_TYPING: StartTypingMessage,
        MessageType.STOP_TYPING: StopTypingMessage,
    }

    message_class = type_class_mapping.get(message_type)

    if not message_class:
        raise ValueError(f"Неизвестный тип сообщения: {message_type}")

    return message_class(login=login, **in_data)
