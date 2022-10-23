from backend.metrics import RequestCounter


CREATE_NEW_CHAT_COUNTER = RequestCounter("create_new_chat", "Количество запросов на создание нового чата")
CHANGE_CHAT_NAME_COUNTER = RequestCounter("change_chat_name", "Количество запросов")
TRY_LEAVE_CHAT_COUNTER = RequestCounter("try_leave_chat", "Количество запросов на попытку выйти из чата")
LEAVE_CHAT_COUNTER = RequestCounter("leave_chat", "Количество запросов на выход из чата")
