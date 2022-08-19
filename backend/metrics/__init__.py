from typing import Optional, Dict

from prometheus_client import Counter


TOTAL_REQUEST_CNT = Counter("total_request", "Количество запросов по всем endpoint's")


class RequestCounter(Counter):
    """Класс счетчика HTTP запросов"""

    def inc(self, amount: float = 1, exemplar: Optional[Dict[str, str]] = None) -> None:
        TOTAL_REQUEST_CNT.inc()
        super().inc(amount, exemplar)
