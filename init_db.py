from loguru import logger

from backend.database import engine
from backend import tables
from backend.database import get_session
from backend.settings import get_settings

tables.Base.metadata.create_all(bind=engine)


def init_db():
    tables.Base.metadata.create_all(bind=engine)
    create_main_chat_if_needed()


def create_main_chat_if_needed():
    session = next(get_session())
    settings = get_settings()

    if _is_main_chat_exist(session=session, settings=settings):
        logger.info("Главный чат уже есть")
    else:
        main_chat = tables.Chat(
            id=settings.main_chat_id,
            name="Главная",
            is_public=True
        )
        session.add(main_chat)
        session.commit()

        logger.info(f"Создан главный чат с id: {settings.main_chat_id}")


def _is_main_chat_exist(session, settings) -> bool:
    return bool(session.query(tables.Chat).where(tables.Chat.id == settings.main_chat_id).first())


if __name__ == '__main__':
    init_db()
