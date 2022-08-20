from loguru import logger
from sqlalchemy.orm import Session

from backend.database import engine
from backend import tables
from backend.database import get_session
from backend.settings import get_settings, Settings
from backend.services.auth import AuthService


def init_db():
    tables.Base.metadata.create_all(bind=engine)

    session = next(get_session())
    settings = get_settings()

    create_admin_if_needed(session=session, settings=settings)
    create_main_chat_if_needed(session=session, settings=settings)


def create_admin_if_needed(session: Session, settings: Settings) -> None:
    if admin := get_admin(session=session):
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

    admin_profile = tables.Profile(user=admin.id)
    session.add(admin_profile)
    session.commit()

    logger.info("Создан админ")


def get_admin(session: Session) -> tables.User | None:
    return session.query(tables.User).where(tables.User.login == "admin").first()


def create_main_chat_if_needed(session: Session, settings: Settings) -> None:
    if is_main_chat_exist(session=session, settings=settings):
        logger.info("Главный чат уже есть")
        return

    admin = get_admin(session=session)

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


def is_main_chat_exist(session: Session, settings: Settings) -> bool:
    return bool(session.query(tables.Chat).where(tables.Chat.id == settings.main_chat_id).first())


if __name__ == '__main__':
    init_db()
