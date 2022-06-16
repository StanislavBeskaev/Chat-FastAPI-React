from collections import OrderedDict

from sqlalchemy import or_, and_
from pydantic import BaseModel

from .. import models
from .. import tables
from ..settings import get_settings
from . import BaseService
from .ws import WSMessageData


class MessageData(WSMessageData):
    message_id: str | None
    avatar_file: str | None

    class Config:
        orm_mode = True


class ChatData(MessageData):
    chat_id: str
    chat_name: str


class Chat(BaseModel):
    chat_name: str
    messages: list[MessageData]


class MessageService(BaseService):
    """Сервис для работы с сообщениями и чатами"""

    # TODO подумать как обойти MAIN, возможно имеет смысл добавлять к нему пользователей при регистрации
    def get_many(self, user: models.User) -> dict[str, Chat]:
        """Получение всех сообщений пользователя по чатам"""
        settings = get_settings()
        messages = (
            self.session
            .query(
                tables.Chat.id.label("chat_id"),
                tables.Chat.name.label("chat_name"),
                tables.Message.id.label("message_id"),
                tables.Message.time.label("time"),
                tables.Message.text.label("text"),
                tables.User.login.label("login"),
                tables.Profile.avatar_file.label("avatar_file")
            )
            .distinct()
            .join(tables.Message, tables.Chat.id == tables.Message.chat_id, isouter=True)
            .join(tables.User, tables.Message.user_id == tables.User.id, isouter=True)
            .join(tables.Profile, tables.User.id == tables.Profile.user, isouter=True)
            .where(
                or_(
                    tables.Chat.id == settings.main_chat_id,
                    and_(
                        tables.Chat.id == tables.ChatMember.chat_id,
                        tables.ChatMember.user_id == user.id
                    )
                )
            )
            .order_by(tables.Message.time)
            .all()
        )

        messages_data = [ChatData(**data) for data in messages]

        return self._convert_messages_to_chats(chats_data=messages_data)

    @staticmethod
    def _convert_messages_to_chats(chats_data: list[ChatData]) -> dict[str, Chat]:
        chats = OrderedDict()

        for chat_data in chats_data:
            if chat_data.chat_id not in chats:
                chats[chat_data.chat_id] = Chat(chat_name=chat_data.chat_name, messages=[])

            if chat_data.message_id:
                chats[chat_data.chat_id].messages.append(MessageData.from_orm(chat_data))

        return chats
