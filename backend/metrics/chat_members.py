from backend.metrics import RequestCounter


GET_CHAT_MEMBERS_COUNTER = RequestCounter("get_chat_members", "Количество запросов на получение участников чата")
ADD_CHAT_MEMBER_COUNTER = RequestCounter("add_chat_member", "Количество запросов на добавление участника к чату")
DELETE_CHAT_MEMBERS_COUNTER = RequestCounter("delete_chat_member", "Количество запросов на удаление участника из чата")
