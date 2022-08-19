from fastapi import (
    APIRouter,
    Depends,
    status,
)

from backend import models
from backend.dependencies import get_current_user
from backend.metrics import contacts as contacts_metrics
from backend.services.contact import ContactService


router = APIRouter(
    prefix='/contacts',
    tags=['contacts'],
)


# TODO документация
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[models.Contact]
)
def get_contacts(user: models.User = Depends(get_current_user), contact_service: ContactService = Depends()):
    """Получение контактов текущего пользователя"""
    contacts_metrics.GET_CONTACTS_CNT.inc()

    return contact_service.get_many(user=user)


# TODO документация
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
    contacts_metrics.CREATE_CONTACT_CNT.inc()

    return contact_service.create(user=user, contact_login=new_contact.login)


# TODO документация
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
    contacts_metrics.DELETE_CONTACT_CNT.inc()

    contact_service.delete(user=user, contact_login=contact_to_delete.login)
    return {"message": f"Контакт {contact_to_delete.login} удалён"}


# TODO документация
@router.get(
    "/{login}",
    status_code=status.HTTP_200_OK,
    response_model=models.Contact
)
def get_contact_info(
    login: str,
    user: models.User = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Получение данных контакта по логину"""
    contacts_metrics.GET_CONTACT_INFO_CNT.inc()

    return contact_service.get_by_login(user=user, contact_login=login)


# TODO документация
@router.put(
    "/",
    status_code=status.HTTP_200_OK
)
def change_contact(
    contact_data: models.ContactChange,
    user: models.User = Depends(get_current_user),
    contact_service: ContactService = Depends()
):
    """Изменение данных контакта"""
    contacts_metrics.CHANGE_CONTACT_CNT.inc()

    contact_service.change(user=user, contact_data=contact_data)
