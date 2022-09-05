import json
import os
from pathlib import Path

from fastapi import FastAPI, Request, WebSocketDisconnect, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from starlette.responses import FileResponse
from starlette_exporter import PrometheusMiddleware, handle_metrics

from backend import api
from backend.init_app import init_app
from backend.services.files import FilesService
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
    init_app()


@app.websocket("/ws/{login}")
async def websocket_endpoint(websocket: WebSocket, login: str):
    """Endpoint для ws соединений от пользователей"""
    manager = WSConnectionManager()
    need_send_online_status_message = not manager.has_user_active_connection(login=login)

    ws_client = WebsocketClient(login=login, websocket=websocket)
    await manager.connect(ws_client)
    logger.info(f"Новое ws соединение от пользователя {login}")
    logger.debug(f"Параметры соединения: {websocket.__dict__}")

    if need_send_online_status_message:
        logger.info(f"У пользователя {login} ещё не было активного соединения, посылаем OnlineMessage")
        online_message = OnlineMessage(login=login)
        await online_message.send_all()
    else:
        logger.info(f"У пользователя {login} уже есть активное соединение, OnlineMessage не посылается")

    try:
        while True:
            raw_message = await websocket.receive_text()
            logger.info(f"Message from {login}: {raw_message}")

            message_dict = json.loads(raw_message)
            new_message = create_message_by_type(
                message_type=message_dict[MESSAGE_TYPE_KEY],
                login=login,
                in_data=message_dict[MESSAGE_DATA_KEY]
            )

            await new_message.send_all()
    except WebSocketDisconnect:
        manager.disconnect(ws_client)
        logger.info(f"disconnect ws: {login}")

        if not manager.has_user_active_connection(login=login):
            logger.info(f"У пользователя {login} нет больше активных соединений, посылаем OfflineMessage")
            offline_message = OfflineMessage(login=login)
            await offline_message.send_all()
        else:
            logger.info(f"У пользователя {login} ещё есть активные соединения, OfflineMessage не посылается")
    except Exception as e:
        logger.error(f"Возникла ошибка в ходе работы с ws: {str(e)}")


fronted_build_folder = Path(os.path.join(Path(__file__).resolve().parent.parent, "frontend", "build"))
templates = Jinja2Templates(directory=fronted_build_folder.as_posix())

app.mount(
    "/static/",
    StaticFiles(directory=os.path.join(fronted_build_folder, "static")),
    name="React App static files",
)


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_react_app_and_files(full_path: str, request: Request):
    """Endpoint для отрисовки React приложения и раздачи файлов"""
    logger.debug(f"serve_react_app, full_path: {full_path}")
    if full_path.startswith("api/files"):
        logger.debug("api/files hit")
        avatar_file_name = full_path.split("/")[-1]
        logger.debug(f"{avatar_file_name=}")
        return FileResponse(path=FilesService.get_file_path(file_name=avatar_file_name), media_type="image/png")
    elif "." in full_path:
        logger.debug("build file hit")
        return FileResponse(path=os.path.join(fronted_build_folder, full_path))
    return templates.TemplateResponse("index.html", {"request": request})
