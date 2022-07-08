from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


Base = declarative_base()


class MessageType(str, Enum):
    """Виды сообщений"""
    TEXT = "TEXT"
    INFO = "INFO"


# TODO подумать над полями
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey("users.id"), index=True)
    refresh_token = Column(String, nullable=False)
    user_agent = Column(String, nullable=False)

    user_rel = relationship(User, backref="tokens")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey("users.id"), index=True)
    avatar_file = Column(String, nullable=True)

    user_rel = relationship(User, backref="profiles")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(String, primary_key=True, autoincrement=False)
    name = Column(String)
    is_public = Column(Boolean, default=False)
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)


class ChatMember(Base):
    __tablename__ = "chat_members"

    id = Column(Integer, primary_key=True)
    chat_id = Column(String, ForeignKey("chats.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, autoincrement=False)
    chat_id = Column(String, ForeignKey("chats.id"), index=True)
    text = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    time = Column(DateTime(timezone=True), server_default=func.now())
    type = Column(String, default=MessageType.TEXT)

    user_rel = relationship(User, backref="messages")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), index=True)
    contact_user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)


class MessageReadStatus(Base):
    __tablename__ = "messages_read_status"

    id = Column(Integer, primary_key=True)
    message_id = Column(String, ForeignKey("messages.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    is_read = Column(Boolean, default=False)
