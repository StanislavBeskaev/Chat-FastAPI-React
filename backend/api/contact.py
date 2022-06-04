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
    status_code=status.HTTP_201_CREATED,
    response_model=models.Contact
)
def create_contact(
    new_contact: models.ContactCreate,
    user: models.User = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Создание нового контакта"""
    return contact_service.create(user=user, contact_login=new_contact.login)


# TODO документация
# TODO тесты
@router.delete(
    "/",
    status_code=status.HTTP_200_OK
)
def delete_contact(
    contact_to_delete: models.ContactDelete,
    user: models.User = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Удаление контакта"""
    contact_service.delete(user=user, contact_login=contact_to_delete.login)

    return {"message": f"Контакт {contact_to_delete.login} удалён"}


# TODO документация
# TODO тесты
@router.get(
    "/{login}",
    status_code=status.HTTP_200_OK,
    response_model=models.Contact
)
def get_contact(
    login: str,
    user: models.User = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Получение данных контакта по логину"""
    return contact_service.get_by_login(user=user, contact_login=login)


# TODO документация
# TODO тесты
@router.put(
    "/",
    status_code=status.HTTP_204_NO_CONTENT
)
def change_contact(
    contact_data: models.ContactChange,
    user: models.User = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Изменение данных контакта"""
    contact_service.change(user=user, contact_data=contact_data)
