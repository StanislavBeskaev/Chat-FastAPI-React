import os
from pathlib import Path
from typing import Generator
from unittest import TestCase

from fastapi.testclient import TestClient
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .. import tables
from ..database import get_session
from ..main import app


TEST_DB_NAME = "test.db"
TEST_SQLALCHEMY_DATABASE_URL = f"sqlite:///./{TEST_DB_NAME}"

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
    session = next(override_get_session())

    @classmethod
    def setUpClass(cls) -> None:
        cls._drop_test_db()
        app.dependency_overrides[get_session] = override_get_session
        tables.Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls) -> None:
        app.dependency_overrides = {}

    @staticmethod
    def _drop_test_db():
        test_db_file_path = os.path.join(Path(__file__).resolve().parent.parent.parent, TEST_DB_NAME)
        os.remove(test_db_file_path)
        logger.info(f"Удалён файл тестовой базы: {test_db_file_path}")
