import asyncio
from collections import OrderedDict

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend import models
from backend.core.time import get_formatted_time
from backend.dao.messages import MessagesDAO
from backend.database import get_session
from backend.services import BaseService
from backend.services.ws import ChangeMessageTextMessage


class MessageService(BaseService):
    """Сервис для работы с сообщениями"""

    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session=session)

        self._messages_dao = MessagesDAO(session=session)

    def get_many(self, user: models.User) -> dict[str, models.ChatMessages]:
        """Получение всех сообщений пользователя по чатам, где пользователь участник"""
        chats_data = self._messages_dao.get_user_messages(user_id=user.id)

        return self._convert_messages_to_chats(chats_data=chats_data)

    def get_chat_messages(self, user: models.User, chat_id: str) -> models.ChatMessages:
        """Получение сообщений конкретного чата"""
        chats_data = self._messages_dao.get_user_chat_messages(user_id=user.id, chat_id=chat_id)
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
        if not new_text:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Сообщение не может быть пустым")

        message = self._messages_dao.get_message_by_id(message_id=message_id)
        if message.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только автор может менять сообщение!")

        message = self._messages_dao.change_message_text(message_id=message_id, new_text=new_text)

        change_message_text_message = ChangeMessageTextMessage(
            chat_id=message.chat_id,
            message_id=message_id,
            message_text=new_text,
            change_time=get_formatted_time(message.change_time) if message.change_time else ""
        )
        asyncio.run(change_message_text_message.send_all())
