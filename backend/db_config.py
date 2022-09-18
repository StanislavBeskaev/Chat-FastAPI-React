from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.settings import get_settings


settings = get_settings()
connection_url = settings.sqlalchemy_connection_url
connect_args = {'check_same_thread': False} if connection_url.startswith("sqlite") else {}
kwargs = {"pool_size": settings.pool_size, "max_overflow": settings.max_overflow} if connection_url.startswith("postgresql") else {}  # noqa

engine = create_engine(
    connection_url,
    connect_args=connect_args,
    **kwargs
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
