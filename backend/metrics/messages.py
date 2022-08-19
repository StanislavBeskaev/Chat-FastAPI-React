from backend.metrics import RequestCounter


GET_ALL_MESSAGES_CNT = RequestCounter("get_all_messages", "Количество запросов на получение сообщений текущего пользователя")  # noqa
GET_CHAT_MESSAGES_CNT = RequestCounter("get_chat_messages", "Количество запросов на получение сообщений конкретного чата")  # noqa
CHANGE_MESSAGE_TEXT_CNT = RequestCounter("change_message_text", "Количество запросов на изменение текста сообщения")
DELETE_MESSAGE_CNT = RequestCounter("delete_message", "Количество запросов на удаление сообщения")
