from loguru import logger

from .. import models
from . import BaseService
from .auth import AuthService


class UserService(BaseService):
    """Сервис для управления пользователями"""

    def change_user_data(self, user_login: str, user_data: models.UserUpdate) -> models.User:
        """Изменение данных пользователя"""
        logger.info(f"Запрос на изменение данных пользователя {user_login}, новые данные: {user_data}")
        auth_service = AuthService(session=self.session)
        user = auth_service.find_user_by_login(login=user_login)

        user.name = user_data.name
        user.surname = user_data.surname

        self.session.add(user)
        self.session.commit()

        return models.User.from_orm(user)
