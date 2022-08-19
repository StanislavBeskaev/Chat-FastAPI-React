from backend.metrics import RequestCounter


CREATE_NEW_CHAT_COUNTER = RequestCounter("create_new_chat", "Количество запросов на создание нового чата")
CHANGE_CHAT_NAME_COUNTER = RequestCounter("change_chat_name", "Количество запросов")