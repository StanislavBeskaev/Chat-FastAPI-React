from loguru import logger

from backend import models
from backend.database import get_session
from backend.dao.messages import MessagesDAO
from backend.services.user import UserService
from backend.services.ws.base_messages import NoAnswerWSMessage


class ReadMessageWSMessage(NoAnswerWSMessage):
    """Сообщение о прочтении"""

    def __init__(self, login: str, **kwargs):
        logger.debug(f"{self.__class__.__name__} инициализация с параметрами: {login=} {kwargs=}")

        # TODO перенести поиск пользователя по логину в UsersDAO
        self._session = next(get_session())
        user_service = UserService(session=self._session)

        read_message_data: models.InReadMessageData = models.InReadMessageData.parse_obj(kwargs)

        messages_dao = MessagesDAO.create()
        messages_dao.mark_message_as_read(
            message_id=read_message_data.message_id,
            user_id=user_service.find_user_by_login(login=login).id
        )

        super().__init__(login=login)
