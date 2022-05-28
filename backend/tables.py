from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


Base = declarative_base()


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

    user_rel = relationship(User, backref="tokens")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey("users.id"), index=True)
    avatar_file = Column(String, nullable=True)

    user_rel = relationship(User, backref="profiles")


# TODO подумать над всеми нужными таблицами для чатов: Chat, ChatMembers, Message и может другие
# TODO тут нужна ссылка на чат сообщения
class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, autoincrement=False)
    text = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    time = Column(DateTime(timezone=True), server_default=func.now())
    type = Column(String, nullable=False)  # TODO тут нужно перечисление
    online_status = Column(String, nullable=False)  # TODO тут нужно перечисление

    user_rel = relationship(User, backref="messages")
