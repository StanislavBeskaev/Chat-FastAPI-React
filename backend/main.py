import json
from datetime import datetime

from fastapi import FastAPI, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from . import api
from .services.ws import WSConnectionManager


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


# TODO убрать после тестов
from fastapi import Depends, Request, WebSocket
from . import models
from .dependencies import get_current_user


@app.get("/api/test")
def test(request: Request, user: models.User = Depends(get_current_user)):
    logger.debug(f"test, user: {user}")
    logger.debug(f"{request.cookies=}")
    return {"message": "test"}


app.mount("/api/static", StaticFiles(directory="files"), name="static")


@app.websocket("/ws/{login}")
async def websocket_endpoint(websocket: WebSocket, login: str):
    manager = WSConnectionManager()
    await manager.connect(websocket)
    logger.debug(f"Новое ws соединение от пользователя {login} {websocket.__dict__}")
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    # TODO сделать разные варианты сообщений
    message = {"time": current_time, "login": login, "text": "Online"}
    await manager.broadcast(json.dumps(message))
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Message from {login}: {data}")

            message = {"time": current_time, "login": login, "text": data}
            logger.debug(f"broadcast message: {message}")
            await manager.broadcast(json.dumps(message))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.debug(f"disconnect ws: {login}")

        message = {"time": current_time, "login": login, "text": "Offline"}
        logger.debug(f"broadcast message: {message}")
        await manager.broadcast(json.dumps(message))
