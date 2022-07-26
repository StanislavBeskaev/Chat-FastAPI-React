from datetime import datetime
from uuid import uuid4

from loguru import logger
from sqlalchemy import and_
from sqlalchemy.orm import Query, aliased

from backend import tables, models
from backend.core.time import get_current_time
from backend.dao import BaseDAO


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

        text_message = models.Message.from_orm(db_message)
        logger.info(f"В базу сохранено текстовое сообщение: {text_message} ")

        return text_message

    def create_unread_messages(self, message: models.Message, chat_members: list[models.User]) -> None:
        """Создание записей не прочитанного сообщения для участников чата"""
        unread_messages = [
            tables.MessageReadStatus(
                message_id=message.id,
                user_id=user.id
            )
            for user in chat_members if user.id != message.user_id
        ]

        self.session.bulk_save_objects(unread_messages)
        self.session.commit()
        logger.info(f"В базу сохранено непрочитанное сообщения {message.id} для пользователей {chat_members}")

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

    def _get_user_chat_messages_query(self, user_id: int) -> Query:
        """Получение запроса для сообщений пользователя, по всем чатам, где пользователь участник"""
        chat_creator = aliased(tables.User)

        messages_query = (
            self.session
            .query(
                tables.Chat.id.label("chat_id"),
                tables.Chat.name.label("chat_name"),
                tables.Message.id.label("message_id"),
                tables.Message.time.label("time"),
                tables.Message.text.label("text"),
                tables.Message.type.label("type"),
                tables.User.login.label("login"),
                chat_creator.login.label("creator"),
                tables.MessageReadStatus.is_read.label("is_read"),
                tables.Message.change_time.label("change_time")
            )
            .distinct()
            .join(tables.Message, tables.Chat.id == tables.Message.chat_id, isouter=True)
            .join(tables.User, tables.Message.user_id == tables.User.id, isouter=True)
            .join(tables.Profile, tables.User.id == tables.Profile.user, isouter=True)
            .join(chat_creator, tables.Chat.creator_id == chat_creator.id)
            .join(
                tables.MessageReadStatus,
                and_(
                    tables.Message.id == tables.MessageReadStatus.message_id,
                    tables.MessageReadStatus.user_id == user_id
                ),
                isouter=True)
            .where(
                and_(
                    tables.Chat.id == tables.ChatMember.chat_id,
                    tables.ChatMember.user_id == user_id
                )
            )
            .order_by(tables.Message.time)
        )

        return messages_query

    def get_user_messages(self, user_id: int) -> list[models.ChatData]:
        """Получение сообщений пользователя по всем чатам, где пользователь участник"""
        messages = (
            self._get_user_chat_messages_query(user_id=user_id)
            .all()
        )
        chats_data = [models.ChatData(**data) for data in messages]

        return chats_data

    def get_user_chat_messages(self, user_id: int, chat_id: str) -> list[models.ChatData]:
        """Получение сообщений конкретного чата"""
        chat_messages = (
            self._get_user_chat_messages_query(user_id=user_id)
            .where(tables.Chat.id == chat_id)
            .all()
        )
        chats_data = [models.ChatData(**data) for data in chat_messages]

        return chats_data

    def get_message_by_id(self, message_id: str) -> tables.Message:
        """Получение сообщения по id"""
        message = (
            self.session
            .query(tables.Message)
            .where(tables.Message.id == message_id)
            .first()
        )

        return message

    def change_message_text(self, message_id: str, new_text: str) -> tables.Message:
        """Изменение текста сообщения"""
        message = self.get_message_by_id(message_id=message_id)
        old_text = message.text
        message.text = new_text
        message.change_time = datetime.now()
        self.session.add(message)
        self.session.commit()

        logger.info(f"Для сообщения {message.id} изменён текст с '{old_text}' на '{new_text}'."
                    f" Время изменения {message.change_time}")

        return message
