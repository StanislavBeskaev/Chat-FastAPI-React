import json

from fastapi import FastAPI, WebSocketDisconnect, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from . import api
from .services.ws import (
    WSConnectionManager,
    WSMessage,
    OnlineMessage,
    OfflineMessage,
    MESSAGE_TYPE_KEY,
    MESSAGE_DATA_KEY
)


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


@app.on_event("startup")
def start():
    logger.info("Старт API")


app.mount("/api/static", StaticFiles(directory="files"), name="static")


@app.websocket("/ws/{login}")
async def websocket_endpoint(websocket: WebSocket, login: str):
    manager = WSConnectionManager()
    await manager.connect(websocket)
    logger.debug(f"Новое ws соединение от пользователя {login} {websocket.__dict__}")
    online_message = OnlineMessage(login=login)
    # TODO позже сделать рассылку по комнатам
    await online_message.send_all()
    try:
        while True:
            message = await websocket.receive_text()
            logger.debug(f"Message from {login}: {message}")

            # TODO расширение, ввести тип и для входящего сообщения, например typing_start, typing_end
            message_dict = json.loads(message)
            new_message = WSMessage.create_message_by_type(
                message_type=message_dict[MESSAGE_TYPE_KEY],
                login=login,
                in_data=message_dict[MESSAGE_DATA_KEY]
            )

            await new_message.send_all()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.debug(f"disconnect ws: {login}")

        offline_message = OfflineMessage(login=login)
        await offline_message.send_all()
