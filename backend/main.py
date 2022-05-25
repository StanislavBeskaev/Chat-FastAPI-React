from fastapi import FastAPI, WebSocketDisconnect, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from . import api
from .services.messages import TextMessage, OnlineMessage, OfflineMessage
from .services.user import UserService
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


app.mount("/api/static", StaticFiles(directory="files"), name="static")


@app.websocket("/ws/{login}")
async def websocket_endpoint(websocket: WebSocket, login: str, user_service: UserService = Depends()):
    manager = WSConnectionManager()
    await manager.connect(websocket)
    logger.debug(f"Новое ws соединение от пользователя {login} {websocket.__dict__}")
    online_message = OnlineMessage(login=login, user_service=user_service)
    # TODO позже сделать рассылку по комнатам
    await online_message.send_all()
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Message from {login}: {data}")

            message = TextMessage(login=login, user_service=user_service, text=data)
            await message.send_all()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.debug(f"disconnect ws: {login}")

        offline_message = OfflineMessage(login=login, user_service=user_service)
        await offline_message.send_all()
