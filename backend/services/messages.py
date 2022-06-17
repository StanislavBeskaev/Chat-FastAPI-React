from collections import OrderedDict

from sqlalchemy import and_
from loguru import logger

from backend import models, tables
from backend.services import BaseService


class MessageService(BaseService):
    """Сервис для работы с сообщениями и чатами"""

    def add_user_to_chat(self, user: models.User, chat_id: str) -> None:
        """Добавление пользователя к чату. Если пользователь уже есть в чате, то ничего не происходит"""
        logger.debug(f"Попытка добавить к чату {chat_id} пользователя {user}")
        if self.is_user_in_chat(user=user, chat_id=chat_id):
            logger.warning(f"В чате {chat_id} уже есть пользователь {user}")
            return

        new_chat_member = tables.ChatMember(
            chat_id=chat_id,
            user_id=user.id
        )

        self.session.add(new_chat_member)
        self.session.commit()

        logger.info(f"К чату {chat_id} добавлен пользователь {user}")

    def is_user_in_chat(self, user: models.User, chat_id: str) -> bool:
        """Есть ли пользователь в чате"""
        candidate = (
            self.session
            .query(tables.ChatMember)
            .where(
                and_(
                    tables.ChatMember.chat_id == chat_id,
                    tables.ChatMember.user_id == user.id
                )
            )
            .first()
        )

        return candidate is not None

    def get_chat_members(self, chat_id: str) -> list[models.User]:
        users_in_chat = (
            self.session
            .query(tables.User)
            .where(
                and_(
                    tables.User.id == tables.ChatMember.user_id,
                    tables.ChatMember.chat_id == chat_id
                )
            )
            .all()
        )

        users = [models.User.from_orm(user) for user in users_in_chat]
        logger.debug(f"Участники чата {chat_id}: {users}")
        return users

    def get_many(self, user: models.User) -> dict[str, models.Chat]:
        """Получение всех сообщений пользователя по чатам"""
        messages = (
            self.session
            .query(
                tables.Chat.id.label("chat_id"),
                tables.Chat.name.label("chat_name"),
                tables.Message.id.label("message_id"),
                tables.Message.time.label("time"),
                tables.Message.text.label("text"),
                tables.User.login.label("login"),
                tables.Profile.avatar_file.label("avatar_file")
            )
            .distinct()
            .join(tables.Message, tables.Chat.id == tables.Message.chat_id, isouter=True)
            .join(tables.User, tables.Message.user_id == tables.User.id, isouter=True)
            .join(tables.Profile, tables.User.id == tables.Profile.user, isouter=True)
            .where(
                and_(
                    tables.Chat.id == tables.ChatMember.chat_id,
                    tables.ChatMember.user_id == user.id
                )
            )
            .order_by(tables.Message.time)
            .all()
        )

        messages_data = [models.ChatData(**data) for data in messages]

        return self._convert_messages_to_chats(chats_data=messages_data)

    @staticmethod
    def _convert_messages_to_chats(chats_data: list[models.ChatData]) -> dict[str, models.Chat]:
        chats = OrderedDict()

        for chat_data in chats_data:
            if chat_data.chat_id not in chats:
                chats[chat_data.chat_id] = models.Chat(chat_name=chat_data.chat_name, messages=[])

            if chat_data.message_id:
                chats[chat_data.chat_id].messages.append(models.MessageData.from_orm(chat_data))

        return chats
