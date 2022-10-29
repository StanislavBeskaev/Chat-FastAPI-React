from backend.metrics import RequestCounter


CHANGE_USER_DATA_COUNTER = RequestCounter("change_user_data", "Количество запросов на изменение данных пользователя")
UPLOAD_AVATAR_COUNTER = RequestCounter("upload_avatar", "Количество запросов на загрузку аватара")
GET_LOGIN_AVATAR_FILE_COUNTER = RequestCounter(
    "get_login_avatar_file", "Количество запросов на получение файла аватара пользователя по логину"
)
GET_LOGIN_AVATAR_FILENAME_COUNTER = RequestCounter(
    "get_login_avatar_filename", "Количество запросов на получение названия файла аватара пользователя по логину"
)
GET_USER_INFO_COUNTER = RequestCounter(
    "get_user_info", "Количество запросов на получение информации о пользователе по логину"
)
