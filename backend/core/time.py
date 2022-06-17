from datetime import datetime

import pytz

from backend.settings import get_settings


def get_current_time() -> datetime:
    settings = get_settings()
    return datetime.now(pytz.timezone(settings.timezone))


def get_formatted_time(value: datetime = get_current_time()) -> str:
    return value.strftime("%d.%m.%y %H:%M")  # TODO подумать над отображением даты
