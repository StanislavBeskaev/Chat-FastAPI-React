from fastapi import (
    APIRouter,
    Depends,
    status,
)

from .. import models
from ..dependencies import get_current_user
from ..services.contact import ContactService


router = APIRouter(
    prefix='/contacts',
    tags=['contacts'],
)


# TODO документация
# TODO тесты
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[models.Contact]
)
def get_contacts(user: models.User = Depends(get_current_user), contact_service: ContactService = Depends()):
    """Получение контактов текущего пользователя"""
    return contact_service.get_many(user=user)


# TODO документация
# TODO тесты
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED
)
def create_contact(
    new_contact: models.ContactCreate,
    user: models.User = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Создание нового контакта"""
    contact_service.create(user=user, contact_login=new_contact.login)

    return {"message": "Контакт добавлен"}