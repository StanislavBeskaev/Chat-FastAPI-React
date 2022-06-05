from typing import Generator, Any
from unittest import TestCase

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .. import tables
from ..database import get_session
from ..main import app


TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_session() -> Generator[Session, None, None]:
    test_session = TestingSessionLocal()
    try:
        yield test_session
    finally:
        test_session.close()


class BaseTestCase(TestCase):
    client = TestClient(app)

    @classmethod
    def setUpClass(cls) -> None:
        app.dependency_overrides[get_session] = override_get_session
        tables.Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls) -> None:
        app.dependency_overrides = {}

    @staticmethod
    def with_id_sort(elements: list[Any]) -> list[Any]:
        return sorted(elements, key=lambda element: element.id, reverse=True)
