from backend.metrics import OutWSCounter, InWSCounter


START_TYPING_OUT_WS_MESSAGE_CNT = OutWSCounter("start_typing_out_ws_message", "Количество исходящих ws сообщений о начале печатания")  # noqa
START_TYPING_IN_WS_MESSAGE_CNT = InWSCounter("start_typing_in_ws_message", "Количество входящих ws сообщений о начале печатания")  # noqa
STOP_TYPING_OUT_WS_MESSAGE_CNT = OutWSCounter("stop_typing_out_ws_message", "Количество исходящих ws сообщений об окончании печатания")  # noqa
STOP_TYPING_IN_WS_MESSAGE_CNT = InWSCounter("stop_typing_in_ws_message", "Количество исходящих ws сообщений об окончании печатания")  # noqa

ONLINE_STATUS_OUT_WS_MESSAGE_CNT = OutWSCounter("online_status_out_ws_message", "Количество исходящих ws сообщений о входе пользователя в систему")  # noqa
OFLINE_STATUS_OUT_WS_MESSAGE_CNT = OutWSCounter("ofline_status_out_ws_message", "Количество исходящих ws сообщений о выходе пользователя из системы")  # noqa

TEXT_IN_WS_MESSAGE_CNT = InWSCounter("text_in_ws_message", "Количество входящих текстовых сообщений")

READ_MESSAGE_IN_WS_MESSAGE_CNT = InWSCounter("read_message_in_ws_message", "Количество входящих сообщений о прочтении сообщения")  # noqa
