from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from . import api


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
from fastapi import Depends, Request
from . import models
from .dependencies import get_current_user


@app.get("/api/test")
def test(request: Request, user: models.User = Depends(get_current_user)):
    logger.debug(f"test, user: {user}")
    logger.debug(f"{request.cookies=}")
    return {"message": "test"}
