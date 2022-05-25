from fastapi import WebSocket
from loguru import logger


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
        if not hasattr(self, "active_connections"):
            self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.debug(f"{self.__class__.__name__} новое ws соединение,"
                     f" в списке уже {len(self.active_connections)} соединений")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_personal_message(message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        logger.debug(f"{self.__class__.__name__} broadcast на {len(self.active_connections)} соединений")
        for connection in self.active_connections:
            await connection.send_text(message)
