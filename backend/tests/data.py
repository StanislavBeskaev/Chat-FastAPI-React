from datetime import datetime

from backend import tables
from backend.services.auth import AuthService

# Данные для тестов
TEST_CHAT_ID = "TEST"
TEST_CHAT_NAME = "Тестовый чат"
SECOND_CHAT_ID = "SECOND"
SECOND_CHAT_NAME = "SECOND_CHAT"
MESSAGES_TIME = datetime(year=2022, month=5, day=9, hour=9, minute=42)

messages = [
    tables.Message(id="1", chat_id=TEST_CHAT_ID, text="Первое", user_id=1, type=tables.MessageType.TEXT, time=MESSAGES_TIME),  # noqa
    tables.Message(id="2", chat_id=TEST_CHAT_ID, text="Как дела?", user_id=1, type=tables.MessageType.TEXT, time=MESSAGES_TIME),  # noqa
    tables.Message(id="3", chat_id=TEST_CHAT_ID, text="куку", user_id=1, type=tables.MessageType.TEXT, time=MESSAGES_TIME),  # noqa
]
messages_read_status = [
    tables.MessageReadStatus(message_id="1", user_id=2, is_read=False),
    tables.MessageReadStatus(message_id="2", user_id=2, is_read=False),
    tables.MessageReadStatus(message_id="3", user_id=2, is_read=False),
]
refresh_tokens = [
    tables.RefreshToken(id=1, user=1, refresh_token="123", user_agent="321"),
    tables.RefreshToken(id=2, user=2, refresh_token="123", user_agent="321"),
]
users = [
    tables.User(id=1, login="user", name="user", surname="surname", password_hash=AuthService.hash_password("password")),  # noqa
    tables.User(id=2, login="user1", name="user1", surname="surname1", password_hash=AuthService.hash_password("password1")),  # noqa
    tables.User(id=3, login="new", name="new", surname="", password_hash=AuthService.hash_password("password2")),
    tables.User(id=4, login="user2", name="user2", surname="surname2", password_hash=AuthService.hash_password("password2")),  # noqa
    tables.User(id=5, login="some", name="some", surname="", password_hash=AuthService.hash_password("password3")),
    tables.User(id=6, login="user3", name="user3", surname="surname3", password_hash=AuthService.hash_password("password3")),  # noqa
    tables.User(id=7, login="user4", name="user4", surname="surname4", password_hash=AuthService.hash_password("password4")),  # noqa
    tables.User(id=8, login="user5", name="user5", surname="surname5", password_hash=AuthService.hash_password("password5")),  # noqa
]
chat_members = [
    tables.ChatMember(id=1, user_id=1, chat_id=TEST_CHAT_ID),
    tables.ChatMember(id=2, user_id=2, chat_id=TEST_CHAT_ID),
    tables.ChatMember(id=3, user_id=3, chat_id=TEST_CHAT_ID),
    tables.ChatMember(id=4, user_id=1, chat_id=SECOND_CHAT_ID),
    tables.ChatMember(id=5, user_id=2, chat_id=SECOND_CHAT_ID),
    tables.ChatMember(id=6, user_id=3, chat_id=SECOND_CHAT_ID),
    tables.ChatMember(id=7, user_id=4, chat_id=SECOND_CHAT_ID),
]
chats = [
    tables.Chat(id=TEST_CHAT_ID, name=TEST_CHAT_NAME, creator_id=1, is_public=False),
    tables.Chat(id=SECOND_CHAT_ID, name=SECOND_CHAT_NAME, creator_id=1, is_public=False),
]
profiles = [
    tables.Profile(id=1, user=1, avatar_file="user:surname.jpeg"),
    tables.Profile(id=2, user=2, avatar_file="user1:surname1.jpeg"),
    tables.Profile(id=3, user=3, avatar_file=""),
    tables.Profile(id=4, user=4, avatar_file=""),
    tables.Profile(id=5, user=5, avatar_file=""),
    tables.Profile(id=6, user=6, avatar_file=""),
    tables.Profile(id=7, user=7, avatar_file=""),
    tables.Profile(id=8, user=8, avatar_file=""),
]
contacts = [
    tables.Contact(id=1, owner_user_id=1, contact_user_id=2, name="user1", surname="surname1"),
    tables.Contact(id=2, owner_user_id=1, contact_user_id=4, name="user2", surname="surname2"),
    tables.Contact(id=3, owner_user_id=1, contact_user_id=6, name="user3", surname="surname3"),
]
