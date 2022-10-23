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
    DELETE_FROM_CHAT = "DELETE_FROM_CHAT"
    READ_MESSAGE = "READ_MESSAGE"
    CHANGE_MESSAGE_TEXT = "CHANGE_MESSAGE_TEXT"
    DELETE_MESSAGE = "DELETE_MESSAGE"
    LEAVE_CHAT = "LEAVE_CHAT"
    DELETE_CHAT = "DELETE_CHAT"


class OnlineStatus(str, Enum):
    """Статусы пользователя в сети"""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
