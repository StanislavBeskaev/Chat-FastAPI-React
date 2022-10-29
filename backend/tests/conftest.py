import copy
from functools import partial

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.testclient import TestClient
import pytest

from backend import models
from backend.dependencies import get_current_user
from backend.settings import get_settings
from backend.db.facade import get_db_facade
from backend.db.mock.facade import MockDBFacade
from backend.main import app
from backend.tests import data as test_data

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')


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
def auth_mocker(mocker):
    mocker.patch(
        "passlib.hash.bcrypt.verify",
        lambda plain_password, hashed_password: plain_password == hashed_password
    )


@pytest.fixture
def client(db_facade, auth_mocker):
    test_client = TestClient(app)
    app.dependency_overrides[get_db_facade] = lambda: db_facade
    app.dependency_overrides[get_current_user] = partial(mock_get_current_user, db_facade=db_facade)

    return test_client


def mock_get_current_user(db_facade, token: str = Depends(oauth2_scheme)) -> models.User:
    """
    Mock зависимость для проверки авторизации пользователя по JWT
    Ожидается token в формате 'login-password'
    """
    not_auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Не валидный токен доступа',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    token_parts = token.split("-")
    if len(token_parts) != 2:
        raise not_auth_exception from None

    login, password = token_parts
    user = db_facade.find_user_by_login(login=login)
    if not user:
        raise not_auth_exception from None

    if login != password:
        raise not_auth_exception from None

    return models.User.from_orm(user)
