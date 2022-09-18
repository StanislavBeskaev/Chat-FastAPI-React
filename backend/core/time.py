from datetime import datetime


def get_current_time() -> datetime:
    return datetime.now()


def get_formatted_time(value: datetime = get_current_time()) -> str:
    """Получение форматированного времени для корректного парсинга на фронте"""
    return value.strftime("%Y-%m-%dT%H:%M:%S")
