from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


# TODO подумать над полями
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String, nullable=False)


# TODO RefreshToken?
class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey("users.id"), index=True)
    refresh_token = Column(String, nullable=False)

    user_rel = relationship(User, backref="tokens")
