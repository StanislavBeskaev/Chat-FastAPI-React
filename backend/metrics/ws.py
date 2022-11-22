from backend.metrics import InWSCounter, OutWSCounter

START_TYPING_OUT_WS_MESSAGE_COUNTER = OutWSCounter(
    "start_typing_out_ws_message", "Количество исходящих ws сообщений о начале печатания"
)
START_TYPING_IN_WS_MESSAGE_COUNTER = InWSCounter(
    "start_typing_in_ws_message", "Количество входящих ws сообщений о начале печатания"
)
STOP_TYPING_OUT_WS_MESSAGE_COUNTER = OutWSCounter(
    "stop_typing_out_ws_message", "Количество исходящих ws сообщений об окончании печатания"
)
STOP_TYPING_IN_WS_MESSAGE_COUNTER = InWSCounter(
    "stop_typing_in_ws_message", "Количество исходящих ws сообщений об окончании печатания"
)

ONLINE_STATUS_OUT_WS_MESSAGE_COUNTER = OutWSCounter(
    "online_status_out_ws_message", "Количество исходящих ws сообщений о входе пользователя в систему"
)
OFFLINE_STATUS_OUT_WS_MESSAGE_COUNTER = OutWSCounter(
    "ofline_status_out_ws_message", "Количество исходящих ws сообщений о выходе пользователя из системы"
)

ADD_CHAT_MEMBER_OUT_WS_MESSAGE_COUNTER = OutWSCounter(
    "add_chat_member_out_ws_message", "Количество исходящих сообщений о добавлении пользователя к чату"
)
DELETE_CHAT_MEMBER_OUT_WS_MESSAGE_COUNTER = OutWSCounter(
    "delete_chat_member_out_ws_message", "Количество исходящих сообщений о удалении пользователя из чата"
)

CHANGE_CHAT_NAME_OUT_WS_MESSAGE_COUNTER = OutWSCounter(
    "change_chat_name_out_ws_message", "Количество исходящих сообщений об изменении названия чата"
)
NEW_CHAT_OUT_WS_MESSAGE_COUNTER = OutWSCounter("new_chat_out_ws_message", "Количество исходящих сообщений о новом чате")

INFO_OUT_WS_MESSAGE_COUNTER = OutWSCounter("info_out_ws_message", "Количество исходящих информационных сообщений")

TEXT_IN_WS_MESSAGE_COUNTER = InWSCounter("text_in_ws_message", "Количество входящих текстовых сообщений")
TEXT_OUT_WS_MESSAGE_COUNTER = OutWSCounter("text_out_ws_message", "Количество исходящих текстовых сообщений")

READ_MESSAGE_IN_WS_MESSAGE_COUNTER = InWSCounter(
    "read_message_in_ws_message", "Количество входящих сообщений о прочтении сообщения"
)
CHANGE_MESSAGE_TEXT_OUT_WS_MESSAGE_COUNTER = OutWSCounter(
    "change_message_text_out_ws_message", "Количество исходящих сообщений об изменении текста сообщения"
)
DELETE_MESSAGE_OUT_WS_MESSAGE_COUNTER = OutWSCounter(
    "delete_message_out_ws_message", "Количество исходящих сообщений об удалении сообщения"
)

LEAVE_CHAT_OUT_WS_MESSAGE_COUNTER = OutWSCounter(
    "leave_chat_out_ws_message", "Количество исходящих сообщений о выходе пользователя из чата"
)
DELETE_CHAT_OUT_WS_MESSAGE_COUNTER = OutWSCounter(
    "delete_chat_out_ws_message", "Количество исходящих сообщений об удалении чата"
)
