from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from loguru import logger

from backend import tables, models
from backend.core.decorators import model_result
from backend.core.time import get_current_time
from backend.db.mock.chat_members import MockChatMembersDAO
from backend.db.mock.chats import MockChatsDAO
from backend.db.mock.users import MockUsersDAO


class MockMessagesDAO:
    """Mock класс для работы с сообщениями в БД"""
    messages: list[tables.Message]
    messages_read_status: list[tables.MessageReadStatus]

    @model_result(models.MessageFull)
    def get_all_messages(self) -> list[models.MessageFull]:
        """Получение всех записей из таблицы сообщений"""
        return self.messages

    @model_result(models.MessageReadStatus)
    def get_all_read_status_messages(self) -> list[models.MessageReadStatus]:
        """Получение всех записей из таблицы информации о прочтении сообщения пользователем"""
        return self.messages_read_status

    def create_text_message(self, text: str, user_id: int, chat_id: str) -> models.Message:
        """Создание текстового сообщения в базе"""
        db_message = tables.Message(
            id=str(uuid4()),
            text=text,
            user_id=user_id,
            time=get_current_time(),
            chat_id=chat_id,
            type=tables.MessageType.TEXT
        )

        self.messages.append(db_message)

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

        self.messages_read_status.extend(unread_messages)
        chat_members_logins = [user.login for user in chat_members]
        logger.info(f"В базу сохранено непрочитанное сообщения {message.id} для пользователей {chat_members_logins}")

    def mark_message_as_read(self, message_id: str, user_id: int) -> None:
        """Пометить, что пользователь прочитал сообщение"""
        logger.debug(f"Запрос на прочтение сообщения: {user_id=} {message_id=}")
        unread_message = self.get_unread_message(message_id=message_id, user_id=user_id)
        if not unread_message:
            logger.warning(f"Пользователь {user_id} попытка пометить прочитанным не существующее сообщение {message_id}")
            return

        unread_message.is_read = True
        logger.debug(f"Сообщение помечено прочитанным: {user_id=} {message_id=}")

    def get_unread_message(self, message_id: str, user_id: int) -> tables.MessageReadStatus | None:
        """Получение объекта информации о прочтении сообщения пользователем"""
        unread_message = next(
            (message_read_status for message_read_status in self.messages_read_status
             if message_read_status.message_id == message_id and message_read_status.user_id == user_id),
            None
        )

        return unread_message

    def create_info_message(self, text: str, user_id: int, chat_id: str) -> models.Message:
        """Создание информационного сообщения в базе"""
        db_message = tables.Message(
            id=str(uuid4()),
            text=text,
            user_id=user_id,
            time=get_current_time(),
            chat_id=chat_id,
            type=tables.MessageType.INFO
        )
        self.messages.append(db_message)

        info_message = models.Message.from_orm(db_message)
        logger.info(f"В базу сохранено информационное сообщение: {info_message} ")

        return info_message

    def _get_user_messages_chat_data(
            self,
            user_id: int,
            chat_members_dao: MockChatMembersDAO,
            chats_dao: MockChatsDAO,
            users_dao: MockUsersDAO
    ) -> list[models.ChatData]:
        """Получение всех сообщений пользователя"""
        user_chat_ids = [
            chat_member.chat_id for chat_member in chat_members_dao.chat_members if chat_member.user_id == user_id
        ]
        chats_data = []
        for chat_id in user_chat_ids:
            chat = chats_dao.get_chat_by_id(chat_id=chat_id)
            chat_messages = [message for message in self.messages if message.chat_id == chat_id]

            if not chat_messages:
                chats_data.append(
                    models.ChatData(
                        chat_id=chat_id,
                        chat_name=chat.name,
                        creator=users_dao.find_user_by_id(user_id=chat.creator_id).login,
                    )
                )

            for message in chat_messages:
                unread_message = self.get_unread_message(message_id=message.id, user_id=user_id)
                chats_data.append(
                    models.ChatData(
                        chat_id=chat_id,
                        chat_name=chat.name,
                        message_id=message.id,
                        text=message.text,
                        time=message.time,
                        type=message.type,
                        login=users_dao.find_user_by_id(user_id=message.user_id).login,
                        creator=users_dao.find_user_by_id(user_id=chat.creator_id).login,
                        is_read=unread_message.is_read if unread_message else True,
                        change_time=message.change_time
                    )
                )

        return chats_data

    def get_user_messages(
            self,
            user_id: int,
            chat_members_dao: MockChatMembersDAO,
            chats_dao: MockChatsDAO,
            users_dao: MockUsersDAO
    ) -> list[models.ChatData]:
        """Получение сообщений пользователя по всем чатам, где пользователь участник"""
        return self._get_user_messages_chat_data(
            user_id=user_id,
            chat_members_dao=chat_members_dao,
            chats_dao=chats_dao,
            users_dao=users_dao
        )

    def get_user_chat_messages(
            self,
            user_id: int,
            chat_id: str,
            chat_members_dao: MockChatMembersDAO,
            chats_dao: MockChatsDAO,
            users_dao: MockUsersDAO
    ) -> list[models.ChatData]:
        """Получение сообщений пользователя по конкретному чату"""
        chat_data = [
            chat_data for chat_data in self._get_user_messages_chat_data(
                user_id=user_id,
                chat_members_dao=chat_members_dao,
                chats_dao=chats_dao,
                users_dao=users_dao
            )
            if chat_data.chat_id == chat_id
        ]
        return chat_data

    def get_message_by_id(self, message_id: str) -> tables.Message:
        """Получение сообщения по id"""
        message = next(
            (message for message in self.messages if message.id == message_id),
            None
        )

        if not message:
            logger.warning(f"Сообщение с id {message_id} не найдено")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Сообщение с id {message_id} не найдено")

        return message

    def change_message_text(self, message_id: str, new_text: str) -> tables.Message:
        """Изменение текста сообщения"""
        message = self.get_message_by_id(message_id=message_id)
        old_text = message.text
        message.text = new_text
        message.change_time = datetime.now()

        logger.info(f"Для сообщения {message.id} изменён текст с '{old_text}' на '{new_text}'."
                    f" Время изменения {message.change_time}")

        return message

    def delete_message(self, message_id: str) -> None:
        """Удаление сообщения из базы"""
        message = self.get_message_by_id(message_id=message_id)
        self.messages.remove(message)
        self.messages_read_status = [
            message_read_status for message_read_status in self.messages_read_status
            if message_read_status.message_id == message_id
        ]

        logger.info(f"Удалено сообщение '{message.text}' c id {message.id},"
                    f"чата {message.chat_id} пользователя {message.user_id}")
