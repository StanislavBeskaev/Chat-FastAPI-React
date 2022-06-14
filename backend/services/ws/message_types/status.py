from abc import ABC, abstractmethod
import random

from ..constants import OnlineStatus, MessageType
from ..time import get_formatted_time
from ..base_message import WSMessageData, BaseWSMessage


class StatusMessageData(WSMessageData):
    """Данные статусного сообщения"""
    online_status: OnlineStatus


class StatusMessageBase(BaseWSMessage, ABC):
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


class OnlineMessage(StatusMessageBase):
    """Сообщение при подключении пользователя"""
    online_status = OnlineStatus.ONLINE

    def _get_text_templates(self) -> list[str]:
        # TODO добавить больше фраз
        online_text_templates = [
            "Пользователь {login} в сети",
            "К нам подкрался {login}",
            "{login} внезапно тут",
            "Пользователь {login} уже онлайн",
            "А вот и {login}",
            "Хорошо, что ты пришёл {login}",
            "Пользователь {login} ворвался в чат",
            "{login} уже тут",
        ]

        return online_text_templates


class OfflineMessage(StatusMessageBase):
    """Сообщение об отключении пользователя"""
    online_status = OnlineStatus.OFFLINE

    def _get_text_templates(self) -> list[str]:
        # TODO добавить больше фраз
        offline_text_templates = [
            "{login} вышел",
            "Куда ты {login}?",
            "{login} offline",
            "Пользователь {login} решил смыться",
            "Стало пусто без {login}",
            "Пока {login}",
        ]

        return offline_text_templates
