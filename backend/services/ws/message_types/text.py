from uuid import uuid4

from loguru import logger

from backend import models
from backend import tables
from backend.database import get_session
from backend.core.time import get_formatted_time, get_current_time
from backend.services.get_chat_members import get_chat_members
from backend.services.user import UserService
from backend.services.ws.constants import MessageType
from backend.services.ws.base_messages import BaseChatWSMessage


class TextMessage(BaseChatWSMessage):
    """Текстовое сообщение"""
    message_type = MessageType.TEXT

    def __init__(self, login: str, **kwargs):
        self._session = next(get_session())
        self._user_service = UserService(session=self._session)

        in_text_message_data: models.InTextMessageData = models.InTextMessageData.parse_obj(kwargs)
        self._text = in_text_message_data.text
        self._chat_id = in_text_message_data.chat_id

        super().__init__(login=login)

    def _get_data(self) -> models.TextMessageData:
        db_message = self._create_db_message()

        data = models.TextMessageData(
            message_id=db_message.id,
            type=self.message_type,
            login=self._login,
            time=get_formatted_time(db_message.time),
            text=self._text,
            chat_id=self._chat_id
        )

        logger.info(f"В базу сохранено текстовое сообщение: {data} ")
        return data

    def _create_db_message(self) -> tables.Message:
        message = tables.Message(
            id=str(uuid4()),
            text=self._text,
            user_id=self._user_service.find_user_by_login(login=self._login).id,
            time=get_current_time(),
            chat_id=self._chat_id,
        )

        self._session.add(message)
        self._session.commit()
        self._session.refresh(message)

        chat_members = get_chat_members(chat_id=self._chat_id)
        unread_messages = [
            tables.MessageReadStatus(
                message_id=message.id,
                user_id=user.id
            )
            for user in chat_members
        ]

        self._session.bulk_save_objects(unread_messages)
        self._session.commit()

        return message
