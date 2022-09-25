import asyncio
from collections import OrderedDict

from fastapi import HTTPException, status
from loguru import logger

from backend import models
from backend.core.time import get_formatted_time
from backend.services import BaseService
from backend.services.ws import ChangeMessageTextMessage, DeleteMessageMessage


class MessageService(BaseService):
    """Сервис для работы с сообщениями"""

    def get_many(self, user: models.User) -> dict[str, models.ChatMessages]:
        """Получение всех сообщений пользователя по чатам, где пользователь участник"""
        logger.debug(f"Запрос всех сообщений от пользователя {user}")
        chats_data = self._db_facade.get_user_messages(user_id=user.id)

        return self._convert_messages_to_chats(chats_data=chats_data)

    def get_chat_messages(self, user: models.User, chat_id: str) -> models.ChatMessages:
        """Получение сообщений конкретного чата"""
        logger.debug(f"Запрос сообщений чата {chat_id} от пользователя {user}")

        # Тут будет 404 если чата с таким id нет
        self._db_facade.get_chat_by_id(chat_id=chat_id)
        chats_data = self._db_facade.get_user_chat_messages(user_id=user.id, chat_id=chat_id)
        chat_messages = self._convert_messages_to_chats(chats_data=chats_data)[chat_id]

        return chat_messages

    @staticmethod
    def _convert_messages_to_chats(chats_data: list[models.ChatData]) -> dict[str, models.ChatMessages]:
        """Агрегация данных о сообщениях по чатам"""
        chats = OrderedDict()

        for chat_data in chats_data:
            if chat_data.chat_id not in chats:
                chats[chat_data.chat_id] = models.ChatMessages(
                    chat_name=chat_data.chat_name,
                    creator=chat_data.creator,
                    messages=[]
                )

            if chat_data.message_id:
                chats[chat_data.chat_id].messages.append(models.MessageData.from_orm(chat_data))

        return chats

    def change_message_text(self, message_id: str, new_text: str, user: models.User) -> None:
        """Изменение текста сообщения"""
        logger.debug(f"Попытка изменения текста сообщения. Входные данные: "
                     f"{message_id=} {new_text=} {user=}")
        if not new_text:
            logger.warning(f"Передан пустой текст для сообщения")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Сообщение не может быть пустым")

        # Тут будет 404 ошибка если сообщения нет
        message = self._db_facade.get_message_by_id(message_id=message_id)

        if message.user_id != user.id:
            logger.warning(f"Только автор может менять сообщение! {message.user_id=} {user.id=}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только автор может менять сообщение!")

        if message.text == new_text:
            logger.warning("Передан тот же текст сообщения что уже есть ничего не делаем")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="У сообщения уже такой текст")

        message = self._db_facade.change_message_text(message_id=message_id, new_text=new_text)

        change_message_text_message = ChangeMessageTextMessage(
            chat_id=message.chat_id,
            message_id=message_id,
            message_text=new_text,
            change_time=get_formatted_time(message.change_time),
            db_facade=self._db_facade
        )
        asyncio.run(change_message_text_message.send_all())

    def delete_message(self, message_id: str, user: models.User) -> None:
        """Удаление сообщения"""
        logger.debug(f"Попытка удаления сообщения c id={message_id} от пользователя {user}")
        # Тут будет 404 ошибка если сообщения нет
        message = self._db_facade.get_message_by_id(message_id=message_id)

        if message.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только автор может удалять сообщение!")

        self._db_facade.delete_message(message_id=message_id)

        delete_message_ws_message = DeleteMessageMessage(
            chat_id=message.chat_id,
            message_id=message_id,
            db_facade=self._db_facade
        )
        asyncio.run(delete_message_ws_message.send_all())
