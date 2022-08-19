from backend.metrics import RequestCounter


REGISTRATION_CNT = RequestCounter("registration", "Количество запросов на регистрацию")
LOGIN_CNT = RequestCounter("login", "Количество запросов на авторизацию")
REFRESH_TOKENS_CNT = RequestCounter("refresh_tokens", "Количество запросов на обновление токенов")
LOGOUT_CNT = RequestCounter("logout", "Количество запросов на выход из системы")
