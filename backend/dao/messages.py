from uuid import uuid4

from loguru import logger

from backend import tables, models
from backend.core.time import get_current_time
from backend.dao import BaseDAO
from backend.dao.chat_members import ChatMembersDAO


class MessagesDAO(BaseDAO):
    """Класс для работы с сообщениями в БД"""

    def create_text_message(self, text: str, user_id: int, chat_id: str) -> models.Message:
        """Создание текстового сообщения в базе"""
        db_message = tables.Message(
            id=str(uuid4()),
            text=text,
            user_id=user_id,
            time=get_current_time(),
            chat_id=chat_id,
        )

        self.session.add(db_message)
        self.session.commit()
        self.session.refresh(db_message)

        self.create_unread_messages(message=db_message)
        text_message = models.Message.from_orm(db_message)
        logger.info(f"В базу сохранено текстовое сообщение: {text_message} ")

        return text_message

    def create_unread_messages(self, message: tables.Message) -> None:
        """Создание записей не прочитанных сообщений"""
        chat_members_dao = ChatMembersDAO.create()
        chat_members = chat_members_dao.get_chat_members(chat_id=message.chat_id)
        unread_messages = [
            tables.MessageReadStatus(
                message_id=message.id,
                user_id=user.id
            )
            for user in chat_members if user.id != message.user_id
        ]

        self.session.bulk_save_objects(unread_messages)
        self.session.commit()
        logger.debug(f"В базу сохранены непрочитанные сообщения: {unread_messages}")

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

    def create_info_message(self, text: str, user_id: int, chat_id: str) -> models.Message:
        db_message = tables.Message(
            id=str(uuid4()),
            text=text,
            user_id=user_id,
            time=get_current_time(),
            chat_id=chat_id,
            type=tables.MessageType.INFO
        )
        self.session.add(db_message)
        self.session.commit()
        self.session.refresh(db_message)

        info_message = models.Message.from_orm(db_message)
        logger.info(f"В базу сохранено информационное сообщение: {info_message} ")

        return info_message
