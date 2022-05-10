from pydantic import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_connection_url: str = "sqlite:///./chat.db"

    jwt_algorithm: str = 'HS256'

    jwt_access_secret: str = "h2*5gHN4"
    jwt_access_expires_s: int = 15

    jwt_refresh_secret: str = "N4;0a1%cvm#da"
    jwt_refresh_expires_s: int = 60 * 60 * 24 * 30


def get_settings() -> Settings:
    return Settings()
