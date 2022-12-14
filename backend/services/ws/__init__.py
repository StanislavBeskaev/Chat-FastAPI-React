from backend.db.interface import DBFacadeInterface
from backend.services.ws.base_messages import BaseOutWSMessage
from backend.services.ws.constants import MESSAGE_DATA_KEY, MESSAGE_TYPE_KEY, MessageType
from backend.services.ws.message_types import (
    AddLoginToChatMessage,
    ChangeChatNameMessage,
    ChangeMessageTextMessage,
    DeleteChatMessage,
    DeleteLoginFromChatMessage,
    DeleteMessageMessage,
    InfoMessage,
    LeaveChatMessage,
    NewChatMessage,
    OfflineMessage,
    OnlineMessage,
    ReadMessageWSMessage,
    StartTypingMessage,
    StopTypingMessage,
    TextMessage,
)


def create_message_by_type(
    message_type: MessageType, login: str, db_facade: DBFacadeInterface, in_data: dict
) -> BaseOutWSMessage:
    type_class_mapping = {
        MessageType.TEXT: TextMessage,
        MessageType.START_TYPING: StartTypingMessage,
        MessageType.STOP_TYPING: StopTypingMessage,
        MessageType.READ_MESSAGE: ReadMessageWSMessage,
    }

    message_class = type_class_mapping.get(message_type)

    if not message_class:
        raise ValueError(f"Неизвестный тип сообщения: {message_type}")

    return message_class(login=login, db_facade=db_facade, **in_data)
