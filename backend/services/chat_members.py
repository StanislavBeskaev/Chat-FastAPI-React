import asyncio

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from loguru import logger

from backend import models
from backend.dao.chat_members import ChatMembersDAO
from backend.dao.chats import ChatsDAO
from backend.dao.messages import MessagesDAO
from backend.dao.users import UsersDAO
from backend.database import get_session
from backend.services import BaseService
from backend.services.ws import InfoMessage, AddLoginToChatMessage, DeleteLoginFromChatMessage
from backend.services.ws_connection_manager import WSConnectionManager


class ChatMembersService(BaseService):
    """Сервис для работы с участниками чатов"""

    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session=session)

        self._chat_members_dao = ChatMembersDAO(session=session)
        self._chats_dao = ChatsDAO(session=session)
        self._messages_dao = MessagesDAO(session=session)
        self._users_dao = UsersDAO(session=session)

    def add_login_to_chat(self, action_user: models.User, login: str, chat_id: str) -> None:
        """Добавление пользователя по логину к чату. Если пользователь уже есть в чате, то ничего не происходит"""
        user = models.User.from_orm(self._users_dao.find_user_by_login(login=login))
        self.add_user_to_chat(user=user, chat_id=chat_id)

        chat = self._chats_dao.get_chat_by_id(chat_id=chat_id)
        add_login_message = self._create_add_login_message(action_user=action_user, login=login, chat_id=chat_id)

        ws_info_add_login_message = InfoMessage(login=action_user.login, info_message=add_login_message)
        asyncio.run(ws_info_add_login_message.send_all())

        add_login_to_chat_message = AddLoginToChatMessage(login=login, chat_id=chat_id, chat_name=chat.name)
        asyncio.run(add_login_to_chat_message.send_all())

    def _create_add_login_message(self, action_user: models.User, login: str, chat_id: str) -> models.Message:
        """Создание сообщения в базе о добавлении пользователя в чат"""
        add_login_message = self._messages_dao.create_info_message(
            text=f"{action_user.login} добавил пользователя {login}",
            user_id=action_user.id,
            chat_id=chat_id
        )
        logger.info(f"В базу сохранено сообщение об добавлении пользователя {login} в чат {chat_id}")

        return add_login_message

    def delete_login_from_chat(self, action_user: models.User, login: str, chat_id: str) -> None:
        """Удаление пользователя по логину из чата"""
        user = models.User.from_orm(self._users_dao.find_user_by_login(login=login))
        chat_member = self._chat_members_dao.find_chat_member(user_id=user.id, chat_id=chat_id)

        chat = self._chats_dao.get_chat_by_id(chat_id=chat_id)
        delete_login_from_chat_message = DeleteLoginFromChatMessage(login=login, chat_id=chat_id, chat_name=chat.name)
        asyncio.run(delete_login_from_chat_message.send_all())

        if not chat_member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Пользователя {login} нет в чате")

        self._chat_members_dao.delete_chat_member(chat_member=chat_member)
        logger.info(f"Из чата {chat_id} удалён пользователь {user}")

        delete_login_message = self._create_delete_login_message(action_user=action_user, login=login, chat_id=chat_id)
        ws_info_delete_login_message = InfoMessage(login=action_user.login, info_message=delete_login_message)
        asyncio.run(ws_info_delete_login_message.send_all())

    def _create_delete_login_message(self, action_user: models.User, login: str, chat_id: str) -> models.Message:
        """Создание сообщения в базе об удалении пользователя из чата"""
        delete_login_message = self._messages_dao.create_info_message(
            text=f"{action_user.login} удалил пользователя {login}",
            user_id=action_user.id,
            chat_id=chat_id
        )
        logger.info(f"В базу сохранено сообщение об удалении пользователя {login} из чата {chat_id}")

        return delete_login_message

    def add_user_to_chat(self, user: models.User, chat_id: str) -> None:
        """Добавление пользователя к чату. Если пользователь уже есть в чате, то ничего не происходит"""
        logger.debug(f"Попытка добавить к чату {chat_id} пользователя {user}")
        if self.is_user_in_chat(user=user, chat_id=chat_id):
            error = f"В чате {chat_id} уже есть пользователь {user}"
            logger.warning(error)
            raise HTTPException(detail=error, status_code=status.HTTP_409_CONFLICT)

        self._chat_members_dao.add_chat_member(user_id=user.id, chat_id=chat_id)
        logger.info(f"К чату {chat_id} добавлен пользователь {user}")

    def is_user_in_chat(self, user: models.User, chat_id: str) -> bool:
        """Есть ли пользователь в чате"""

        return self._chat_members_dao.find_chat_member(user_id=user.id, chat_id=chat_id) is not None

    def get_chat_members_with_online_status(self, chat_id: str) -> list[models.ChatMemberWithOnlineStatus]:
        """Получение информации об участниках чата и их онлайн статусе"""
        chat_members = self._chat_members_dao.get_chat_members(chat_id=chat_id)
        active_logins = WSConnectionManager().get_active_logins()

        chat_members_with_online_status = [
            models.ChatMemberWithOnlineStatus(
                login=member.login,
                is_online=member.login in active_logins
            )
            for member in chat_members
        ]

        return chat_members_with_online_status
