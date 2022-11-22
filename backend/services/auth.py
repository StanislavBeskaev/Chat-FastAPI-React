from fastapi import Depends, HTTPException, status
from loguru import logger
from passlib.hash import bcrypt
from pydantic import ValidationError

from backend import models
from backend.db.facade import get_db_facade
from backend.db.interface import DBFacadeInterface
from backend.services import BaseService
from backend.services.chat_members import ChatMembersService
from backend.services.token import TokenService
from backend.settings import get_settings


class AuthService(BaseService):
    """Сервис авторизации и регистрации"""

    def __init__(self, db_facade: DBFacadeInterface = Depends(get_db_facade)):
        super().__init__(db_facade=db_facade)
        self._token_service = TokenService(db_facade=db_facade)
        self._chat_members_service = ChatMembersService(db_facade=db_facade)

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Хеширование пароля"""
        return bcrypt.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Соответствие пароля и хеша"""
        return bcrypt.verify(plain_password, hashed_password)

    def register_new_user(self, user_data: models.UserCreate, user_agent: str) -> models.Tokens:
        """Регистрация нового пользователя"""
        logger.debug(
            f"Попытка регистрации нового пользователя c данными:"
            f" login={user_data.login}, name={user_data.name}, surname={user_data.surname}"
        )
        if self._db_facade.find_user_by_login(login=user_data.login):
            logger.warning(f"Пользователь с логином '{user_data.login}' уже существует")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким логином уже существует"
            )

        new_user = self._create_new_user(user_data=user_data)
        tokens = self._token_service.generate_tokens(user=new_user, user_agent=user_agent)

        return tokens

    def login_user(self, login: str, password: str, user_agent: str) -> models.Tokens:
        """Авторизация пользователя"""
        logger.debug(f"Попытка авторизации с данными: {login=} {user_agent=}")
        user = self._db_facade.find_user_by_login(login)
        if not user:
            message = "Пользователь с таким логином не найден"
            logger.warning(message)
            raise HTTPException(status_code=404, detail=message)

        if not self.verify_password(plain_password=password, hashed_password=user.password_hash):
            logger.warning(f"Попытка авторизации с неверным паролем для пользователя {user.id}")
            raise HTTPException(status_code=401, detail="Неверный пароль")

        tokens = self._token_service.generate_tokens(user=models.User.from_orm(user), user_agent=user_agent)
        logger.info(f"Пользователь {login} успешно авторизован")
        return tokens

    def refresh_tokens(self, refresh_token: str | None, user_agent: str) -> models.Tokens:
        """Обновление токенов"""
        logger.debug(f"Попытка обновление токенов: {refresh_token=} {user_agent=}")
        if not refresh_token:
            logger.warning("refresh токен не передан, обновление не выполняется")
            raise HTTPException(status_code=401, detail="Не валидный refresh_token")

        user_data = self._token_service.verify_refresh_token(token=refresh_token)
        refresh_token_from_db = self._db_facade.find_refresh_token_by_token(token=refresh_token, user_agent=user_agent)

        if not user_data or not refresh_token_from_db:
            logger.debug(f"Не удалось обновить токены, {user_data=}, {refresh_token_from_db=}")
            raise HTTPException(status_code=401, detail="Не удалось обновить токены")

        try:
            user = models.User.from_orm(self._db_facade.find_user_by_id(user_id=user_data.id))
        except ValidationError as e:
            logger.warning(f"Не удалось получить пользователя по id={user_data.id}: {str(e)}")
            raise HTTPException(status_code=401, detail="Не удалось обновить токены")

        tokens = self._token_service.generate_tokens(user=user, user_agent=user_agent)

        logger.debug("Токены успешно обновлены")
        return tokens

    def logout(self, refresh_token: str | None, user_agent: str) -> None:
        """Выход из системы"""
        logger.debug(f"Попытка выхода из системы, refresh_token: {refresh_token} ")
        if not refresh_token:
            logger.warning("refresh токен не передан, выход не возможен")
            raise HTTPException(status_code=401, detail="Не валидный refresh_token")

        user_data = self._token_service.verify_refresh_token(token=refresh_token)

        self._token_service.delete_refresh_token(token=refresh_token, user_agent=user_agent)
        logger.info(f"Пользователь '{user_data.login}' выполнен выход из системы")

    def _create_new_user(self, user_data: models.UserCreate) -> models.User:
        """Создание нового пользователя"""
        new_user = self._db_facade.create_user(
            login=user_data.login,
            password_hash=self.hash_password(user_data.password),
            name=user_data.name,
            surname=user_data.surname,
        )

        self._db_facade.create_user_profile(user_id=new_user.id)

        settings = get_settings()
        self._chat_members_service.add_user_to_chat(user=new_user, chat_id=settings.main_chat_id)

        return new_user
