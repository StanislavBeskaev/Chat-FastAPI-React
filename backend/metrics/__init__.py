from typing import Optional, Dict

from loguru import logger
from prometheus_client import Counter


TOTAL_REQUEST_CNT = Counter("total_request", "Количество запросов по всем endpoint's")
TOTAL_WS_MESSAGES_CNT = Counter("total_ws_messages", "Количество всех ws сообщений")
IN_WS_MESSAGES_CNT = Counter("in_ws_messages", "Количество входящих ws сообщений")
OUT_WS_MESSAGES_CNT = Counter("out_ws_messages", "Количество исходящих ws сообщений")


class RequestCounter(Counter):
    """Класс счётчика HTTP запросов"""

    def inc(self, amount: float = 1, exemplar: Optional[Dict[str, str]] = None) -> None:
        TOTAL_REQUEST_CNT.inc(amount=amount)
        logger.info(f"TOTAL_REQUEST_CNT.inc {amount}")
        super().inc(amount, exemplar)


class WSCounter(Counter):
    """Класс счётчика ws сообщений"""

    def inc(self, amount: float = 1, exemplar: Optional[Dict[str, str]] = None) -> None:
        TOTAL_WS_MESSAGES_CNT.inc(amount=amount)
        logger.info(f"TOTAL_WS_MESSAGES_CNT.inc {amount}")
        super().inc(amount, exemplar)


class InWSCounter(WSCounter):
    """Класс счётчика входящих ws сообщений"""
    def inc(self, amount: float = 1, exemplar: Optional[Dict[str, str]] = None) -> None:
        IN_WS_MESSAGES_CNT.inc(amount=amount)
        logger.info(f"IN_WS_MESSAGES_CNT.inc {amount}")
        super().inc(amount, exemplar)


class OutWSCounter(WSCounter):
    """Класс счётчика исходящих ws сообщений"""

    def inc(self, amount: float = 1, exemplar: Optional[Dict[str, str]] = None) -> None:
        OUT_WS_MESSAGES_CNT.inc(amount=amount)
        logger.info(f"OUT_WS_MESSAGES_CNT.inc {amount}")
        super().inc(amount, exemplar)
