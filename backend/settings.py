from pathlib import Path, PosixPath

from pydantic import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_connection_url: str = "sqlite:///./data/chat.db"
    pool_size: int = 20
    max_overflow: int = 30

    jwt_algorithm: str = 'HS256'

    jwt_access_secret: str = "h2*5gHN4"
    jwt_access_expires_s: int = 60 * 15

    jwt_refresh_secret: str = "N4;0a1%cvm#da"
    jwt_refresh_expires_s: int = 60 * 60 * 24 * 30

    import_time_delta_s: int = - 3 * 3600

    main_chat_id = "MAIN"
    admin_password = "admin"
    base_dir: str | PosixPath = Path(__file__).resolve().parent.parent


def get_settings() -> Settings:
    return Settings()
