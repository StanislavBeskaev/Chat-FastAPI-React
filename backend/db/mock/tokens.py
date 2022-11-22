from backend import models, tables
from backend.core.decorators import model_result


class MockTokensDAO:
    """Mock класс для работы с токенами в БД"""

    refresh_tokens: list[tables.RefreshToken]

    def delete_all_refresh_tokens(self) -> None:
        """Удаление всех refresh токенов. Нужен для тестов"""
        self.refresh_tokens = []

    @model_result(models.RefreshToken)
    def get_all_refresh_tokens(self) -> list[models.RefreshToken]:
        """Получение всех записей таблицы refresh токенов"""
        return self.refresh_tokens

    def find_refresh_token_by_user(self, user_id: int, user_agent: str) -> tables.RefreshToken | None:
        """Поиск refresh токена по пользователю и user_agent"""
        refresh_token = next(
            (token for token in self.refresh_tokens if token.user == user_id and token.user_agent == user_agent), None
        )

        return refresh_token

    def find_refresh_token_by_token(self, token: str, user_agent: str) -> tables.RefreshToken | None:
        """Поиск refresh токена по токену и user_agent"""
        refresh_token = next(
            (tkn for tkn in self.refresh_tokens if tkn.refresh_token == token and tkn.user_agent == user_agent), None
        )

        return refresh_token

    def create_refresh_token(self, user_id: int, refresh_token: str, user_agent: str) -> tables.RefreshToken:
        """Создание refresh токена"""
        token = tables.RefreshToken(
            id=max([token.id for token in self.refresh_tokens]) + 1,
            user=user_id,
            refresh_token=refresh_token,
            user_agent=user_agent,
        )
        self.refresh_tokens.append(token)
        return token

    @staticmethod
    def update_refresh_token(token: tables.RefreshToken, new_refresh_token: str) -> tables.RefreshToken:
        """Обновление refresh токена"""
        token.refresh_token = new_refresh_token
        return token

    def delete_refresh_token(self, token: str, user_agent: str) -> None:
        """Удаление refresh токена"""
        refresh_token = self.find_refresh_token_by_token(token=token, user_agent=user_agent)
        if refresh_token:
            self.refresh_tokens.remove(refresh_token)
