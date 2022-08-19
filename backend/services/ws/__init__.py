from .base_messages import BaseOutWSMessage
from .constants import MESSAGE_TYPE_KEY, MESSAGE_DATA_KEY, MessageType
from .message_types import (
    OnlineMessage,
    OfflineMessage,
    StartTypingMessage,
    TextMessage,
    StopTypingMessage,
    NewChatMessage,
    ChangeChatNameMessage,
    InfoMessage,
    AddLoginToChatMessage,
    DeleteLoginFromChatMessage,
    ReadMessageWSMessage,
    ChangeMessageTextMessage,
    DeleteMessageMessage,
)


def create_message_by_type(message_type: MessageType, login: str, in_data: dict) -> BaseOutWSMessage:
    type_class_mapping = {
        MessageType.TEXT: TextMessage,
        MessageType.START_TYPING: StartTypingMessage,
        MessageType.STOP_TYPING: StopTypingMessage,
        MessageType.READ_MESSAGE: ReadMessageWSMessage,
    }

    message_class = type_class_mapping.get(message_type)

    if not message_class:
        raise ValueError(f"Неизвестный тип сообщения: {message_type}")

    return message_class(login=login, **in_data)
