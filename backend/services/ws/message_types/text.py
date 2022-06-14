from uuid import uuid4

from loguru import logger
from pydantic import BaseModel, Field

from ....database import get_session
from .... import tables
from ...auth import AuthService
from ...user import UserService
from ..constants import MessageType
from ..time import get_formatted_time, get_current_time
from ..base_message import WSMessageData, BaseWSMessage


class TextMessageData(WSMessageData):
    """Данные текстового сообщения"""
    message_id: str
    chat_id: str
    avatar_file: str | None  # TODO подумать как доставлять файл аватара на frontend


class InTextMessageData(BaseModel):
    """Данные входящего текстового сообщения"""
    chat_id: str = Field(alias="chatId")
    text: str | None


class TextMessage(BaseWSMessage):
    """Текстовое сообщение"""
    message_type = MessageType.TEXT

    def __init__(self, login: str, **kwargs):
        self._session = next(get_session())

        in_text_message_data: InTextMessageData = InTextMessageData.parse_obj(kwargs)
        self._text = in_text_message_data.text
        self._chat_id = in_text_message_data.chat_id

        super().__init__(login=login)

    def _get_data(self) -> TextMessageData:
        db_message = self._create_db_message()

        user_service = UserService(session=self._session)
        data = TextMessageData(
            message_id=db_message.id,
            type=self.message_type,
            login=self._login,
            time=get_formatted_time(db_message.time),
            text=self._text,
            chat_id=self._chat_id,
            avatar_file=user_service.get_avatar_by_login(self._login)
        )

        logger.info(f"В базу сохранено текстовое сообщение: {data} ")
        return data

    def _create_db_message(self) -> tables.Message:
        auth_service = AuthService(session=self._session)
        message = tables.Message(
            id=str(uuid4()),
            text=self._text,
            user_id=auth_service.find_user_by_login(login=self._login).id,
            time=get_current_time(),
            chat_id=self._chat_id,
        )

        self._session.add(message)
        self._session.commit()
        self._session.refresh(message)

        return message
