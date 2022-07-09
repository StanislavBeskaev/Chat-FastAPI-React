from uuid import uuid4

from loguru import logger

from backend import tables
from backend.core.time import get_current_time
from backend.services.get_chat_members import get_chat_members
from backend.dao import BaseDAO


class MessagesDAO(BaseDAO):
    """Класс для работы с сообщениями в БД"""

    def create_text_message(self, text: str, user_id: int, chat_id: str) -> tables.Message:
        """Создание текстового сообщения в базе"""
        message = tables.Message(
            id=str(uuid4()),
            text=text,
            user_id=user_id,
            time=get_current_time(),
            chat_id=chat_id,
        )

        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)

        self.create_unread_messages(message=message)

        return message

    def create_unread_messages(self, message: tables.Message) -> None:
        """Создание записей не прочитанных сообщений"""
        # TODO для всех кроме текущего пользователя
        chat_members = get_chat_members(chat_id=message.chat_id)
        unread_messages = [
            tables.MessageReadStatus(
                message_id=message.id,
                user_id=user.id
            )
            for user in chat_members
        ]

        self.session.bulk_save_objects(unread_messages)
        self.session.commit()

    def mark_message_as_read(self, message_id: str, user_id: int) -> None:
        """Пометить, что пользователь прочитал сообщение"""
        logger.debug(f"Запрос на прочтение сообщения: {user_id=} {message_id=}")
        # TODO проверка на существование сообщения?
        unread_message = self._get_unread_message(message_id=message_id, user_id=user_id)
        unread_message.is_read = True

        self.session.add(unread_message)
        self.session.commit()

        logger.debug(f"Сообщение помечено прочитанным: {user_id=} {message_id=}")

    def _get_unread_message(self, message_id: str, user_id: int) -> tables.MessageReadStatus:
        unread_message = (
            self.session
            .query(tables.MessageReadStatus)
            .where(tables.MessageReadStatus.message_id == message_id)
            .where(tables.MessageReadStatus.user_id == user_id)
            .first()
        )

        return unread_message
