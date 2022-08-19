from loguru import logger

from backend import models
from backend.dao.messages import MessagesDAO
from backend.dao.users import UsersDAO
from backend.metrics import ws as ws_metrics
from backend.services.ws.base_messages import NoAnswerWSMessage, InWSMessageMixin


class ReadMessageWSMessage(InWSMessageMixin, NoAnswerWSMessage):
    """Сообщение о прочтении сообщения"""
    in_metrics_counter = ws_metrics.READ_MESSAGE_IN_WS_MESSAGE_CNT

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
