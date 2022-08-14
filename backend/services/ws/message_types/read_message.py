from loguru import logger

from backend import models
from backend.dao.messages import MessagesDAO
from backend.dao.users import UsersDAO
from backend.services.ws.base_messages import NoAnswerWSMessage


class ReadMessageWSMessage(NoAnswerWSMessage):
    """Сообщение о прочтении"""

    def __init__(self, login: str, **kwargs):
        logger.debug(f"{self.__class__.__name__} инициализация с параметрами: {login=} {kwargs=}")

        read_message_data: models.InReadMessageData = models.InReadMessageData.parse_obj(kwargs)

        messages_dao = MessagesDAO.create()
        users_dao = UsersDAO.create()

        messages_dao.mark_message_as_read(
            message_id=read_message_data.message_id,
            user_id=users_dao.find_user_by_login(login=login).id
        )

        super().__init__(login=login)
