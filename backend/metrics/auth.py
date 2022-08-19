from backend.metrics import RequestCounter


REGISTRATION_COUNTER = RequestCounter("registration", "Количество запросов на регистрацию")
LOGIN_COUNTER = RequestCounter("login", "Количество запросов на авторизацию")
REFRESH_TOKENS_COUNTER = RequestCounter("refresh_tokens", "Количество запросов на обновление токенов")
LOGOUT_COUNTER = RequestCounter("logout", "Количество запросов на выход из системы")
