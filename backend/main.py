import json

from fastapi import FastAPI, WebSocketDisconnect, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from starlette_exporter import PrometheusMiddleware, handle_metrics

from backend import api
from backend.init_db import init_db
from backend.metrics import InWSCounter
from backend.services.ws import (
    OnlineMessage,
    OfflineMessage,
    MESSAGE_TYPE_KEY,
    MESSAGE_DATA_KEY,
    create_message_by_type,
)
from backend.services.ws_connection_manager import WSConnectionManager, WebsocketClient


app = FastAPI(
        title='API приложения для общения',
        description='Приложение для общения',
        version='0.1.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)


@app.on_event("startup")
def start():
    logger.info("Старт API")
    init_db()


app.mount("/api/static", StaticFiles(directory="files"), name="static")
COMMON_IN_WS_CNT = InWSCounter("ws_in", "Входящее ws сообщение")  # TODO подумать надо ли тут это?


@app.websocket("/ws/{login}")
async def websocket_endpoint(websocket: WebSocket, login: str):
    """Endpoint для ws соединений от пользователей"""
    manager = WSConnectionManager()
    ws_client = WebsocketClient(login=login, websocket=websocket)
    await manager.connect(ws_client)
    logger.debug(f"Новое ws соединение от пользователя {login} {websocket.__dict__}")
    online_message = OnlineMessage(login=login)
    await online_message.send_all()
    try:
        while True:
            raw_message = await websocket.receive_text()
            logger.debug(f"Message from {login}: {raw_message}")
            COMMON_IN_WS_CNT.inc()  # TODO  сделать класс для входящих сообщений, что бы в конструкторе было inc

            message_dict = json.loads(raw_message)
            new_message = create_message_by_type(
                message_type=message_dict[MESSAGE_TYPE_KEY],
                login=login,
                in_data=message_dict[MESSAGE_DATA_KEY]
            )

            await new_message.send_all()
    except WebSocketDisconnect:
        manager.disconnect(ws_client)
        logger.debug(f"disconnect ws: {login}")

        offline_message = OfflineMessage(login=login)
        await offline_message.send_all()
    except Exception as e:
        logger.error(f"Возникла ошибка в ходе работы с ws: {str(e)}")
