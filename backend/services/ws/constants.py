from enum import Enum


MESSAGE_TYPE_KEY = "type"
MESSAGE_DATA_KEY = "data"


class MessageType(str, Enum):
    """Типы сообщений"""
    TEXT = "TEXT"
    STATUS = "STATUS"
    START_TYPING = "START_TYPING"
    STOP_TYPING = "STOP_TYPING"
    NEW_CHAT = "NEW_CHAT"
    CHANGE_CHAT_NAME = "CHANGE_CHAT_NAME"
    ADD_TO_CHAT = "ADD_TO_CHAT"


class OnlineStatus(str, Enum):
    """Статусы пользователя в сети"""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
