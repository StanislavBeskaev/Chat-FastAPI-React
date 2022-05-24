from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .settings import get_settings


engine = create_engine(
    get_settings().sqlalchemy_connection_url,
    connect_args={'check_same_thread': False},
)

Session = sessionmaker(
    engine,
    autocommit=False,
    autoflush=False,
)


def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()
