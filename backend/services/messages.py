from collections import OrderedDict

from fastapi import Depends
from sqlalchemy.orm import Session

from backend import models
from backend.dao.messages import MessagesDAO
from backend.database import get_session
from backend.services import BaseService


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
