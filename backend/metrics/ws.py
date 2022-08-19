from backend.metrics import OutWSCounter


START_TYPING_OUT_WS_MESSAGE_CNT = OutWSCounter("start_typing_out_ws_message", "Количество исходящих ws сообщений о начале печатания")  # noqa
STOP_TYPING_OUT_WS_MESSAGE_CNT = OutWSCounter("stop_typing_out_ws_message", "Количество исходящих ws сообщений об окончании печатания")  # noqa

ONLINE_STATUS_OUT_WS_MESSAGE_CNT = OutWSCounter("online_status_out_ws_message", "Количество исходящих ws сообщений о входе пользователя в систему")  # noqa
OFLINE_STATUS_OUT_WS_MESSAGE_CNT = OutWSCounter("ofline_status_out_ws_message", "Количество исходящих ws сообщений о выходе пользователя из системы")  # noqa
