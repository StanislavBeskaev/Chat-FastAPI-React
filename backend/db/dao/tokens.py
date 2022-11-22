from backend import models, tables
from backend.core.decorators import model_result
from backend.db.dao.base_dao import BaseDAO


class TokensDAO(BaseDAO):
    """Класс для работы с токенами в БД"""

    @model_result(models.RefreshToken)
    def get_all_refresh_tokens(self) -> list[models.RefreshToken]:
        """Получение всех записей таблицы refresh токенов"""
        db_refresh_tokens = self.session.query(tables.RefreshToken).all()
        return db_refresh_tokens

    def find_refresh_token_by_user(self, user_id: int, user_agent: str) -> tables.RefreshToken | None:
        """Поиск refresh токена по пользователю и user_agent"""
        refresh_token = (
            self.session.query(tables.RefreshToken)
            .filter(tables.RefreshToken.user == user_id)
            .filter(tables.RefreshToken.user_agent == user_agent)
            .first()
        )

        return refresh_token

    def find_refresh_token_by_token(self, token: str, user_agent: str) -> tables.RefreshToken | None:
        """Поиск refresh токена по токену и user_agent"""
        refresh_token = (
            self.session.query(tables.RefreshToken)
            .filter(tables.RefreshToken.refresh_token == token)
            .filter(tables.RefreshToken.user_agent == user_agent)
            .first()
        )

        return refresh_token

    def create_refresh_token(self, user_id: int, refresh_token: str, user_agent: str) -> tables.RefreshToken:
        """Создание refresh токена"""
        token = tables.RefreshToken(user=user_id, refresh_token=refresh_token, user_agent=user_agent)

        self.session.add(token)
        self.session.commit()

        return token

    def update_refresh_token(self, token: tables.RefreshToken, new_refresh_token: str) -> tables.RefreshToken:
        """Обновление refresh токена"""
        token.refresh_token = new_refresh_token
        self.session.add(token)
        self.session.commit()

        return token

    def delete_refresh_token(self, token: str, user_agent: str) -> None:
        """Удаление refresh токена"""
        refresh_token = self.find_refresh_token_by_token(token=token, user_agent=user_agent)
        self.session.delete(refresh_token)
        self.session.commit()
