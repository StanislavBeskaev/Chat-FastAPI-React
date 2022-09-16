from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .settings import get_settings


connection_url = get_settings().sqlalchemy_connection_url
connect_args = {'check_same_thread': False} if connection_url.startswith("sqlite") else {}

engine = create_engine(
    connection_url,
    connect_args=connect_args,
)

Session = sessionmaker(
    engine,
    autocommit=False,
    autoflush=False,
)


def get_session():
    """Получение сессии БД"""
    session = Session()
    try:
        yield session
    finally:
        session.close()
