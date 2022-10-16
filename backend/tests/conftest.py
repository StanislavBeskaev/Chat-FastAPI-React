import copy

from fastapi.testclient import TestClient
import pytest

from backend.settings import get_settings
from backend.db.facade import get_db_facade
from backend.db.mock.facade import MockDBFacade
from backend.main import app
from backend.tests import data as test_data


@pytest.fixture()
def settings():
    return get_settings()


@pytest.fixture
def db_facade():
    mock_db_facade = MockDBFacade()
    mock_db_facade.chat_members_dao.chat_members = copy.deepcopy(test_data.chat_members)
    mock_db_facade.chats_dao.chats = copy.deepcopy(test_data.chats)
    mock_db_facade.messages_dao.messages = copy.deepcopy(test_data.messages)
    mock_db_facade.messages_dao.messages_read_status = copy.deepcopy(test_data.messages_read_status)
    mock_db_facade.tokens_dao.refresh_tokens = copy.deepcopy(test_data.refresh_tokens)
    mock_db_facade.users_dao.users = copy.deepcopy(test_data.users)
    mock_db_facade.users_dao.profiles = copy.deepcopy(test_data.profiles)
    mock_db_facade.contacts_dao.contacts = copy.deepcopy(test_data.contacts)
    yield mock_db_facade


@pytest.fixture
def client(db_facade):
    test_client = TestClient(app)
    app.dependency_overrides[get_db_facade] = lambda: db_facade

    return test_client
