from backend import models
from backend.dao.chat_members import ChatMembersDAO
from backend.dao.messages import MessagesDAO
from backend.dao.users import UsersDAO
from backend.database import get_session
from backend.core.time import get_formatted_time
from backend.services.ws.constants import MessageType
from backend.services.ws.base_messages import BaseChatWSMessage


class TextMessage(BaseChatWSMessage):
    """Текстовое сообщение"""
    message_type = MessageType.TEXT

    def __init__(self, login: str, **kwargs):
        self._session = next(get_session())

        in_text_message_data: models.InTextMessageData = models.InTextMessageData.parse_obj(kwargs)
        self._text = in_text_message_data.text
        self._chat_id = in_text_message_data.chat_id

        super().__init__(login=login)

    def _get_data(self) -> models.TextMessageData:
        message = self._create_db_message()

        data = models.TextMessageData(
            message_id=message.id,
            type=self.message_type,
            login=self._login,
            time=get_formatted_time(message.time),
            text=self._text,
            chat_id=self._chat_id
        )

        return data

    def _create_db_message(self) -> models.Message:
        messages_dao = MessagesDAO(session=self._session)
        users_dao = UsersDAO(session=self._session)

        message = messages_dao.create_text_message(
            text=self._text,
            user_id=users_dao.find_user_by_login(login=self._login).id,
            chat_id=self._chat_id
        )
        chat_members_dao = ChatMembersDAO(session=self._session)
        messages_dao.create_unread_messages(
            message=message,
            chat_members=chat_members_dao.get_chat_members(chat_id=self._chat_id)
        )

        return message
