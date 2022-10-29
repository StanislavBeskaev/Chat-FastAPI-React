import asyncio

from fastapi import HTTPException, status
from loguru import logger

from backend import models
from backend.services import BaseService
from backend.services.ws import InfoMessage, AddLoginToChatMessage, DeleteLoginFromChatMessage
from backend.services.ws_connection_manager import WSConnectionManager


class ChatMembersService(BaseService):
    """Сервис для работы с участниками чатов"""

    def add_login_to_chat(self, action_user: models.User, login: str, chat_id: str) -> None:
        """Добавление пользователя по логину к чату. Если пользователь уже есть в чате, то ничего не происходит"""
        logger.debug(f"Пользователь {action_user.login} попытка добавить пользователя {login} к чату {chat_id}")
        # Тут будет 404 ошибка если такого чата нет
        chat = self._db_facade.get_chat_by_id(chat_id=chat_id)

        if not self.is_user_in_chat(user=action_user, chat_id=chat_id):
            logger.warning(f"Пользователь {action_user.login} не находится в чате {chat_id},"
                           f" добавление другого пользователя не выполняется")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Вы не участник чата {chat_id}")

        db_user = self._db_facade.find_user_by_login(login=login)
        if not db_user:
            raise HTTPException(status_code=404, detail=f"Пользователя с логином {login} не существует")
        user = models.User.from_orm(db_user)

        self.add_user_to_chat(user=user, chat_id=chat_id)

        add_login_message = self._create_add_login_message(action_user=action_user, login=login, chat_id=chat_id)
        self._notify_about_add_login_to_chat(
            action_user=action_user,
            add_login_message=add_login_message,
            added_login=login,
            chat=chat
        )

    def delete_login_from_chat(self, action_user: models.User, login: str, chat_id: str) -> None:
        """Удаление пользователя по логину из чата"""
        logger.debug(f"Попытка удалить пользователя {login} из чата {chat_id} пользователем {action_user}")
        if not self._is_user_chat_creator(chat_id=chat_id, user=action_user):
            logger.warning(f"Пользователь {action_user.login} не является создателем чата {chat_id},"
                           f" удаление пользователя {login} из чата не выполняется")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только создатель может удалять из чата")

        db_user = self._db_facade.find_user_by_login(login=login)
        if not db_user:
            raise HTTPException(status_code=404, detail=f"Пользователя с логином {login} не существует")
        user = models.User.from_orm(db_user)

        # Тут будет 404 если чата нет
        chat = self._db_facade.get_chat_by_id(chat_id=chat_id)
        chat_member = self._db_facade.find_chat_member(user_id=user.id, chat_id=chat_id)
        if not chat_member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Пользователя {login} нет в чате")

        delete_login_from_chat_message = DeleteLoginFromChatMessage(
            login=login,
            chat_id=chat_id,
            chat_name=chat.name,
            db_facade=self._db_facade
        )
        asyncio.run(delete_login_from_chat_message.send_all())

        self._db_facade.delete_chat_member(chat_member=chat_member)
        logger.info(f"Из чата {chat_id} удалён пользователь {user}")

        delete_login_message = self._create_delete_login_message(action_user=action_user, login=login, chat_id=chat_id)
        ws_info_delete_login_message = InfoMessage(
            login=action_user.login,
            info_message=delete_login_message,
            db_facade=self._db_facade
        )
        asyncio.run(ws_info_delete_login_message.send_all())

    def add_user_to_chat(self, user: models.User, chat_id: str) -> None:
        """
        Добавление пользователя к чату. Если пользователь уже есть в чате, то raise HTTPException 409
        Предполагается, что пользователь и чат существуют
        """
        logger.debug(f"Попытка добавить к чату {chat_id} пользователя {user}")
        if self.is_user_in_chat(user=user, chat_id=chat_id):
            error = f"В чате {chat_id} уже есть пользователь {user.login}"
            logger.warning(error)
            raise HTTPException(detail=error, status_code=status.HTTP_409_CONFLICT)

        self._db_facade.add_chat_member(user_id=user.id, chat_id=chat_id)
        logger.info(f"К чату {chat_id} добавлен пользователь {user}")

    def is_user_in_chat(self, user: models.User, chat_id: str) -> bool:
        """Есть ли пользователь в чате"""

        return self._db_facade.find_chat_member(user_id=user.id, chat_id=chat_id) is not None

    def get_chat_members_with_online_status(self, chat_id: str, user: models.User) -> list[models.ChatMemberWithOnlineStatus]:  # noqa
        """Получение информации об участниках чата и их онлайн статусе"""
        logger.debug(f"Запрос на получение участников чата {chat_id} от пользователя {user.login}")
        # Если такого чата нет, то 404
        self._db_facade.get_chat_by_id(chat_id=chat_id)

        if not self.is_user_in_chat(user=user, chat_id=chat_id):
            logger.warning(f"Пользователь {user.login} не является участником чата {chat_id},"
                           f" участники чата не высылаются")
            raise HTTPException(status_code=403, detail=f"Вы не участник чата {chat_id}")

        chat_members = self._db_facade.get_chat_members(chat_id=chat_id)
        active_logins = WSConnectionManager().get_active_logins()
        chat_members_with_online_status = [
            models.ChatMemberWithOnlineStatus(
                login=member.login,
                is_online=member.login in active_logins
            )
            for member in chat_members
        ]

        return chat_members_with_online_status

    def _create_add_login_message(self, action_user: models.User, login: str, chat_id: str) -> models.Message:
        """Создание сообщения в базе о добавлении пользователя в чат"""
        add_login_message = self._db_facade.create_info_message(
            text=f"{action_user.login} добавил пользователя {login}",
            user_id=action_user.id,
            chat_id=chat_id
        )
        logger.info(f"В базу сохранено сообщение об добавлении пользователя {login} в чат {chat_id}")

        return add_login_message

    def _notify_about_add_login_to_chat(
            self,
            action_user: models.User,
            add_login_message: models.Message,
            added_login: str,
            chat: models.Chat
    ):
        """Рассылка ws уведомлений о добавлении пользователя в чат"""
        ws_info_add_login_message = InfoMessage(
            login=action_user.login,
            info_message=add_login_message,
            db_facade=self._db_facade
        )
        asyncio.run(ws_info_add_login_message.send_all())

        add_login_to_chat_message = AddLoginToChatMessage(
            login=added_login,
            chat_id=chat.id,
            chat_name=chat.name,
            db_facade=self._db_facade
        )
        asyncio.run(add_login_to_chat_message.send_all())

    def _is_user_chat_creator(self, chat_id: str, user: models.User) -> bool:
        """Является ли пользователь создателем чата"""
        chat = self._db_facade.get_chat_by_id(chat_id=chat_id)

        return chat.creator_id == user.id

    def _create_delete_login_message(self, action_user: models.User, login: str, chat_id: str) -> models.Message:
        """Создание сообщения в базе об удалении пользователя из чата"""
        delete_login_message = self._db_facade.create_info_message(
            text=f"{action_user.login} удалил пользователя {login}",
            user_id=action_user.id,
            chat_id=chat_id
        )
        logger.info(f"В базу сохранено сообщение об удалении пользователя {login} из чата {chat_id}")

        return delete_login_message
