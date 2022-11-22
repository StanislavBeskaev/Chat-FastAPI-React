from loguru import logger

from backend import models
from backend.db.interface import DBFacadeInterface
from backend.metrics import ws as ws_metrics
from backend.services.ws.base_messages import InWSMessageMixin, NoAnswerWSMessage


class ReadMessageWSMessage(InWSMessageMixin, NoAnswerWSMessage):
    """Сообщение о прочтении сообщения"""

    in_metrics_counter = ws_metrics.READ_MESSAGE_IN_WS_MESSAGE_COUNTER

    def __init__(self, login: str, db_facade: DBFacadeInterface, **kwargs):
        logger.debug(f"{self.__class__.__name__} инициализация с параметрами: {login=} {kwargs=}")
        read_message_data: models.InReadMessageData = models.InReadMessageData.parse_obj(kwargs)
        db_facade.mark_message_as_read(
            message_id=read_message_data.message_id, user_id=db_facade.find_user_by_login(login=login).id
        )

        super().__init__(login=login, db_facade=db_facade)
