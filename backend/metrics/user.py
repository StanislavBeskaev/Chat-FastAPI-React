from backend.metrics import RequestCounter


CHANGE_USER_DATA_CNT = RequestCounter("change_user_data", "Количество запросов на изменение данных пользователя")
UPLOAD_AVATAR_CNT = RequestCounter("upload_avatar", "Количество запросов на загрузку аватара")
GET_LOGIN_AVATAR_FILE_CNT = RequestCounter("get_login_avatar_file", "Количество запросов на получение файла аватара пользователя по логину") # noqa
GET_LOGIN_AVATAR_FILENAME_CNT = RequestCounter("get_login_avatar_filename", "Количество запросов на получение названия файла аватара пользователя по логину") # noqa
GET_USER_INFO_CNT = RequestCounter("get_user_info", "Количество запросов на получение информации о пользователе по логину") # noqa
