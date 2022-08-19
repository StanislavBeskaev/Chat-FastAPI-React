from backend.metrics import RequestCounter


CREATE_NEW_CHAT_CNT = RequestCounter("create_new_chat", "Количество запросов на создание нового чата")
CHANGE_CHAT_NAME_CNT = RequestCounter("change_chat_name", "Количество запросов")