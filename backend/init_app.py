import os
import shutil

from loguru import logger
from sqlalchemy.orm import Session

from backend.database import engine
from backend import tables
from backend.database import get_session
from backend.settings import get_settings, Settings
from backend.services.auth import AuthService
from backend.services.files import check_files_folder, IMAGES_FOLDER, FilesService


ADMIN_AVATAR = "admin.png"


@check_files_folder
def init_app():
    """Инициализация приложения"""
    logger.info("init_app start")
    _copy_admin_avatar_to_files()
    _init_db()
    logger.info("Инициализация приложения выполнена")


def _copy_admin_avatar_to_files():
    admin_avatar_in_files = FilesService.get_file_path(ADMIN_AVATAR)
    if os.path.exists(admin_avatar_in_files):
        logger.info("Аватарка админа уже в files")
        return

    settings = get_settings()
    shutil.copyfile(
        src=os.path.join(settings.base_dir, IMAGES_FOLDER, ADMIN_AVATAR),
        dst=admin_avatar_in_files
    )
    logger.info(f"Аватарка админа скопирована в {admin_avatar_in_files}")


def _init_db():
    logger.info("_init_db start")
    tables.Base.metadata.create_all(bind=engine)

    session = next(get_session())
    settings = get_settings()

    _create_admin_if_needed(session=session, settings=settings)
    _create_main_chat_if_needed(session=session, settings=settings)


def _create_admin_if_needed(session: Session, settings: Settings) -> None:
    if admin := _get_admin(session=session):
        logger.info("Админ уже существует")
        admin.password_hash = AuthService.hash_password(password=settings.admin_password)
        session.commit()
        logger.info("Для админа изменён пароль на текущий")
        return

    admin = tables.User(
        login="admin",
        name="admin",
        surname="admin",
        password_hash=AuthService.hash_password(password=settings.admin_password)
    )

    session.add(admin)
    session.commit()

    admin_profile = tables.Profile(user=admin.id, avatar_file=ADMIN_AVATAR)
    session.add(admin_profile)
    session.commit()

    logger.info("Создан админ")


def _get_admin(session: Session) -> tables.User | None:
    return session.query(tables.User).where(tables.User.login == "admin").first()


def _create_main_chat_if_needed(session: Session, settings: Settings) -> None:
    if _is_main_chat_exist(session=session, settings=settings):
        logger.info("Главный чат уже есть")
        return

    admin = _get_admin(session=session)

    main_chat = tables.Chat(
        id=settings.main_chat_id,
        name="Главная",
        is_public=True,
        creator_id=admin.id
    )
    session.add(main_chat)
    session.add(
        tables.ChatMember(chat_id=settings.main_chat_id, user_id=admin.id)
    )
    session.commit()

    logger.info(f"Создан главный чат с id: {settings.main_chat_id}")
    logger.info(f"Админ добавлен в главный чат как участник")


def _is_main_chat_exist(session: Session, settings: Settings) -> bool:
    return bool(session.query(tables.Chat).where(tables.Chat.id == settings.main_chat_id).first())
