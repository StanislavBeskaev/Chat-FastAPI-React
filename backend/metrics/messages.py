from backend.metrics import RequestCounter


GET_ALL_MESSAGES_COUNTER = RequestCounter(
    "get_all_messages", "Количество запросов на получение сообщений текущего пользователя"
)
GET_CHAT_MESSAGES_COUNTER = RequestCounter(
    "get_chat_messages", "Количество запросов на получение сообщений конкретного чата"
)
CHANGE_MESSAGE_TEXT_COUNTER = RequestCounter("change_message_text", "Количество запросов на изменение текста сообщения")
DELETE_MESSAGE_COUNTER = RequestCounter("delete_message", "Количество запросов на удаление сообщения")
