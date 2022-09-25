from datetime import datetime

import pytz

from backend.settings import get_settings


def get_current_time() -> datetime:
    settings = get_settings()
    return datetime.now(pytz.timezone(settings.timezone))


def get_formatted_time(value: datetime = get_current_time()) -> str:
    """Получение форматированного времени для корректного парсинга на фронте"""
    return value.strftime("%Y-%m-%dT%H:%M:%S")
