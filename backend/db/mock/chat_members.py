from backend import models, tables
from backend.core.decorators import model_result
from backend.db.mock.users import MockUsersDAO


class MockChatMembersDAO:
    """Mock Класс для работы с участниками чатов в БД"""

    chat_members: list[tables.ChatMember]

    @model_result(models.ChatMemberFull)
    def get_all_chat_members(self) -> list[models.ChatMemberFull]:
        """Получение всех записей таблицы участников чатов"""
        return self.chat_members

    @model_result(models.User)
    def get_chat_members(self, chat_id: str, users_dao: MockUsersDAO) -> list[models.User]:
        """Получение пользователей - участников чата"""
        chat_members_user_ids = [member.user_id for member in self.chat_members if member.chat_id == chat_id]
        chat_members_users = [user for user in users_dao.users if user.id in chat_members_user_ids]
        return chat_members_users

    def find_chat_member(self, user_id: int, chat_id: str) -> tables.ChatMember | None:
        """Поиск участника чата"""
        chat_member = next(
            (member for member in self.chat_members if member.user_id == user_id and member.chat_id == chat_id), None
        )
        return chat_member

    def add_chat_member(self, user_id: int, chat_id: str) -> None:
        """Добавление участника к чату"""
        new_chat_member = tables.ChatMember(
            id=max([chat_member.id for chat_member in self.chat_members]) + 1, chat_id=chat_id, user_id=user_id
        )
        self.chat_members.append(new_chat_member)

    def delete_chat_member(self, chat_member: tables.ChatMember) -> None:
        """Удаление участника из чата"""
        self.chat_members.remove(chat_member)

    def delete_all_members_from_chat(self, chat_id: str) -> None:
        """Удаление всех участников чата"""
        self.chat_members = [chat_member for chat_member in self.chat_members if chat_member.chat_id != chat_id]
