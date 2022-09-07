from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend import tables
from backend.database import get_session
from backend.dao.chats import ChatsDAO
from backend.dao.chat_members import ChatMembersDAO
from backend.dao.users import UsersDAO
from backend.main import app
from backend.init_app import ADMIN_AVATAR
from backend.services.auth import AuthService
from backend.settings import get_settings, Settings
from backend.tests.base import override_get_session, drop_test_db, test_engine


TEST_ADMIN_PASSWORD = "password"


def new_admin_password_get_settings() -> Settings:
    return Settings(
        admin_password=TEST_ADMIN_PASSWORD
    )


class TestStartup(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        drop_test_db()
        app.dependency_overrides[get_session] = override_get_session

    @classmethod
    def tearDownClass(cls) -> None:
        app.dependency_overrides = {}

    @patch(target="backend.init_app.get_session", new=override_get_session)
    @patch(target="backend.init_app.engine", new=test_engine)
    def test_startup(self):
        test_session = next(override_get_session())

        with TestClient(app):
            self._check_admin_and_main_chat(test_session=test_session, settings=get_settings())
            self._check_all_tables_created(test_session=test_session)

        get_settings_patcher = patch(target="backend.init_app.get_settings", new=new_admin_password_get_settings)
        get_settings_patcher.start()
        # Поменяли пароль у админа, проверяем что состояние системы такое же и пароль у админа новый
        with TestClient(app):
            self._check_second_app_startup(test_session=test_session, settings=new_admin_password_get_settings())
        get_settings_patcher.stop()

    def _check_admin_and_main_chat(self, test_session: Session, settings: Settings):
        test_users_dao = UsersDAO(session=test_session)
        test_chats_dao = ChatsDAO(session=test_session)
        test_chat_members_dao = ChatMembersDAO(session=test_session)

        admin = test_users_dao.find_user_by_login(login="admin")
        self.assertIsNotNone(admin)
        self.assertEqual(admin.name, "admin")
        self.assertEqual(admin.surname, "admin")
        self.assertTrue(AuthService.verify_password(
            plain_password=settings.admin_password,
            hashed_password=admin.password_hash
        ))

        admin_profile = test_users_dao.get_profile_by_login(login="admin")
        self.assertEqual(admin_profile.user, admin.id)
        self.assertEqual(admin_profile.avatar_file, ADMIN_AVATAR)

        main_chat = test_chats_dao.get_chat_by_id(settings.main_chat_id)
        self.assertEqual(main_chat.name, "Главная")
        self.assertEqual(main_chat.creator_id, admin.id)

        admin_main_chat_member = test_chat_members_dao.find_chat_member(
            user_id=admin.id, chat_id=settings.main_chat_id
        )
        self.assertIsNotNone(admin_main_chat_member)

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

    def _check_second_app_startup(self, test_session: Session, settings: Settings):
        self._check_admin_and_main_chat(test_session=test_session, settings=settings)

        users_cnt = test_session.query(tables.User.id).count()
        self.assertEqual(users_cnt, 1)
        chats_count = test_session.query(tables.Chat.id).count()
        self.assertEqual(chats_count, 1)
        chat_members_count = test_session.query(tables.ChatMember).count()
        self.assertEqual(chat_members_count, 1)
