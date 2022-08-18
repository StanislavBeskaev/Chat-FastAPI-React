from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend import tables
from backend.database import get_session
from backend.dao.chats import ChatsDAO
from backend.dao.users import UsersDAO
from backend.main import app
from backend.settings import get_settings
from backend.tests.base import override_get_session, drop_test_db, test_engine


class TestStartup(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        drop_test_db()
        app.dependency_overrides[get_session] = override_get_session

    @classmethod
    def tearDownClass(cls) -> None:
        app.dependency_overrides = {}

    @patch(target="backend.init_db.get_session", new=override_get_session)
    @patch(target="backend.init_db.engine", new=test_engine)
    def test_startup(self):
        test_session = next(override_get_session())

        with TestClient(app):
            self._check_admin_and_main_chat(test_session=test_session)
            self._check_all_tables_created(test_session=test_session)

        # TODO повторный вазов with TestClient(app): смена пароля админа в settings что бы проверить,
        #  что у админа меняется пароль и чат всё ещё один - главный

    def _check_admin_and_main_chat(self, test_session: Session):
        settings = get_settings()
        test_users_dao = UsersDAO(session=test_session)
        test_chats_dao = ChatsDAO(session=test_session)
        admin = test_users_dao.find_user_by_login(login="admin")
        self.assertIsNotNone(admin)
        self.assertEqual(admin.name, "admin")
        self.assertEqual(admin.surname, "admin")

        main_chat = test_chats_dao.get_chat_by_id(settings.main_chat_id)
        self.assertEqual(main_chat.name, "Главная")
        self.assertEqual(main_chat.creator_id, admin.id)

    def _check_all_tables_created(self, test_session: Session):
        tables_to_check = [
            tables.User,
            tables.RefreshToken,
            tables.Profile,
            tables.Chat,
            tables.ChatMember,
            tables.Message,
            tables.Contact,
            tables.MessageReadStatus,
        ]
        table_names_to_check = sorted([table.__tablename__ for table in tables_to_check])

        created_tables_cursor_results = test_session.execute("""
            select name
              from sqlite_master
             where type = "table"
        """)

        created_tables = sorted([result[0] for result in created_tables_cursor_results])
        self.assertEqual(len(created_tables), len(tables_to_check))
        self.assertEqual(created_tables, table_names_to_check)
