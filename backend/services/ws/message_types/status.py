from abc import ABC, abstractmethod
import random

from backend import models
from backend.core.time import get_formatted_time
from backend.metrics import ws as ws_metrics
from backend.services.ws.base_messages import BaseWSMessage
from backend.services.ws.constants import OnlineStatus, MessageType


class StatusMessageData(models.WSMessageData):
    """Данные статусного сообщения"""
    online_status: OnlineStatus


class BaseStatusMessage(BaseWSMessage, ABC):
    """Базовый класс статусного сообщения"""
    message_type = MessageType.STATUS
    online_status = None

    def _get_data(self) -> StatusMessageData:
        data = StatusMessageData(
            type=self.message_type,
            login=self._login,
            text=self._get_status_message_text(),
            time=get_formatted_time(),
            online_status=self.online_status
        )

        return data

    def _get_status_message_text(self) -> str:
        return random.choice(self._get_text_templates()).format(login=self._login)

    @abstractmethod
    def _get_text_templates(self) -> list[str]:
        pass


class OnlineMessage(BaseStatusMessage):
    """Сообщение при подключении пользователя"""
    online_status = OnlineStatus.ONLINE
    out_metrics_counter = ws_metrics.ONLINE_STATUS_OUT_WS_MESSAGE_CNT

    def _get_text_templates(self) -> list[str]:
        online_text_templates = [
            "Пользователь {login} в сети",
            "К нам подкрался {login}",
            "{login} внезапно тут",
            "Пользователь {login} уже онлайн",
            "А вот и {login}",
            "Хорошо, что ты пришёл {login}",
            "Пользователь {login} ворвался в чат",
            "{login} уже тут",
            "{login} online",
            "{login} присоединился",
        ]

        return online_text_templates


class OfflineMessage(BaseStatusMessage):
    """Сообщение об отключении пользователя"""
    online_status = OnlineStatus.OFFLINE
    out_metrics_counter = ws_metrics.OFLINE_STATUS_OUT_WS_MESSAGE_CNT

    def _get_text_templates(self) -> list[str]:
        offline_text_templates = [
            "{login} вышел",
            "Куда ты {login}?",
            "{login} offline",
            "Пользователь {login} решил смыться",
            "Стало пусто без {login}",
            "Пока {login}",
            "Как же мы без {login}...",
        ]

        return offline_text_templates
