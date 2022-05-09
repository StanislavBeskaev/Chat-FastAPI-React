from fastapi import (
    APIRouter,
    Depends,
    status,
)


router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


# TODO реализовать
@router.get("/registration",)
def registration():
    """Регистрация нового пользователя"""
    return {"message": "Тут будет регистрация"}
