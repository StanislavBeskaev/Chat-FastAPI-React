from dataclasses import dataclass

from fastapi import WebSocket
from loguru import logger
from prometheus_client import Counter


@dataclass
class WebsocketClient:
    """Клиент ws соединения"""

    login: str
    websocket: WebSocket


class WSConnectionManager:
    """Singleton для обслуживания websocket соединений"""

    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            logger.info(f"Создан instance {cls.__name__}")
            cls.__instance = super().__new__(cls)
        else:
            logger.debug(f"Взят текущий экземпляр {cls.__name__}")

        return cls.__instance

    def __init__(self):
        if not hasattr(self, "active_clients"):
            self.active_clients: list[WebsocketClient] = []

    async def connect(self, ws_client: WebsocketClient):
        """Подключение клиента"""
        await ws_client.websocket.accept()
        self.active_clients.append(ws_client)
        logger.debug(
            f"{self.__class__.__name__} новое ws соединение" f" в списке уже {len(self.active_clients)} соединений"
        )

    def disconnect(self, ws_client: WebsocketClient):
        """Отключение клиента"""
        self.active_clients.remove(ws_client)

    async def broadcast(self, message: str, out_metrics_counter: Counter):
        """Рассылка сообщения на всех подключённых клиентов"""
        logger.debug(
            f"{self.__class__.__name__} broadcast на {len(self.active_clients)} соединений:"
            f" {', '.join([client.login for client in self.active_clients])}"
        )
        for ws_client in self.active_clients:
            await ws_client.websocket.send_text(message)
            out_metrics_counter.inc()

    async def send_message_to_logins(self, logins: list[str], message: str, out_metrics_counter: Counter):
        """Отправка сообщения клиентам по списку логинов"""
        ws_clients_to_send = [ws_client for ws_client in self.active_clients if ws_client.login in logins]
        logins_to_send = [client.login for client in ws_clients_to_send]
        logger.debug(f"{self.__class__.__name__}, рассылка на клиентов: {logins_to_send} сообщения {message}")

        for ws_client in ws_clients_to_send:
            await ws_client.websocket.send_text(message)
            out_metrics_counter.inc()

    def get_active_logins(self) -> list[str]:
        """Получение списка активных логинов"""
        return [client.login for client in self.active_clients]

    def has_user_active_connection(self, login: str) -> bool:
        """Есть ли у пользователя с логином login активное подключение"""
        return login in self.get_active_logins()
