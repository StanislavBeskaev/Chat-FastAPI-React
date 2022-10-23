from fastapi import Depends

from backend import models, tables
from backend.db.interface import DBFacadeInterface
from backend.db.dao import (
    ChatsDAO,
    ChatMembersDAO,
    ContactsDAO,
    MessagesDAO,
    TokensDAO,
    UsersDAO,
)
from backend.db_config import Session, get_session


# TODO наверно нужен классовый метод для создания фасада
class DBFacade(DBFacadeInterface):
    """Фасад для работы с базой данных"""

    def __init__(self, session: Session = Depends(get_session)):
        self._session = session
        self._users_dao = UsersDAO(session=session)
        self._tokens_dao = TokensDAO(session=session)
        self._chats_dao = ChatsDAO(session=session)
        self._chat_members_dao = ChatMembersDAO(session=session)
        self._messages_dao = MessagesDAO(session=session)
        self._contacts_dao = ContactsDAO(session=session)

    def get_all_users(self) -> list[models.User]:
        """Получение всех записей таблицы пользователей"""
        return self._users_dao.get_all_users()

    def get_all_profiles(self) -> list[models.Profile]:
        """Получение всех записей таблицы профилей"""
        return self._users_dao.get_all_profiles()

    def create_user(self, login: str, password_hash: str, name: str, surname: str) -> models.User:
        """Создание пользователя"""
        return self._users_dao.create_user(login=login, password_hash=password_hash, name=name, surname=surname)

    def create_user_profile(self, user_id) -> None:
        """Создание профиля для пользователя"""
        self._users_dao.create_user_profile(user_id=user_id)

    def find_user_by_login(self, login: str) -> tables.User | None:
        """Поиск пользователя по login"""
        return self._users_dao.find_user_by_login(login=login)

    def find_user_by_id(self, user_id: int) -> tables.User | None:
        """Поиск пользователя по id"""
        return self._users_dao.find_user_by_id(user_id=user_id)

    def get_user_info(self, login: str) -> models.User:
        """Получение информации и пользователе"""
        return self._users_dao.get_user_info(login=login)

    def change_user_data(self, login: str, name: str, surname: str) -> models.User:
        """Изменение данных пользователя"""
        return self._users_dao.change_user_data(login=login, name=name, surname=surname)

    def get_profile_by_login(self, login: str) -> models.Profile:
        """Нахождение профайла пользователя по логину пользователя"""
        return self._users_dao.get_profile_by_login(login=login)

    def set_avatar_file(self, user_id: int, avatar_file: str) -> None:
        """Установка имени файла аватара для пользователя"""
        self._users_dao.set_avatar_file(user_id=user_id, avatar_file=avatar_file)

    def get_used_avatar_files(self) -> list[str]:
        """Получение названий используемых файлов аватаров"""
        return self._users_dao.get_used_avatar_files()

    def get_all_refresh_tokens(self) -> list[models.RefreshToken]:
        """Получение всех записей таблицы refresh токенов"""
        return self._tokens_dao.get_all_refresh_tokens()

    def find_refresh_token_by_user(self, user_id: int, user_agent: str) -> tables.RefreshToken | None:
        """Поиск refresh токена по пользователю и user_agent"""
        return self._tokens_dao.find_refresh_token_by_user(user_id=user_id, user_agent=user_agent)

    def find_refresh_token_by_token(self, token: str, user_agent: str) -> tables.RefreshToken | None:
        """Поиск refresh токена по токену и user_agent"""
        return self._tokens_dao.find_refresh_token_by_token(token=token, user_agent=user_agent)

    def create_refresh_token(self, user_id: int, refresh_token: str, user_agent: str) -> tables.RefreshToken:
        """Создание refresh токена"""
        return self._tokens_dao.create_refresh_token(user_id=user_id, refresh_token=refresh_token, user_agent=user_agent)  # noqa

    def update_refresh_token(self, token: tables.RefreshToken, new_refresh_token: str) -> tables.RefreshToken:
        """Обновление refresh токена"""
        return self._tokens_dao.update_refresh_token(token=token, new_refresh_token=new_refresh_token)

    def delete_refresh_token(self, token: str, user_agent: str) -> None:
        """Удаление refresh токена"""
        self._tokens_dao.delete_refresh_token(token=token, user_agent=user_agent)

    def get_all_chats(self) -> list[models.Chat]:
        """Получение всех записей из таблицы чатов"""
        return self._chats_dao.get_all_chats()

    def get_chat_by_id(self, chat_id: str) -> models.Chat:
        """Получение чата по id"""
        return self._chats_dao.get_chat_by_id(chat_id=chat_id)

    def create_chat(self, chat_name: str, creator_id: int) -> models.Chat:
        """Создание нового чата"""
        return self._chats_dao.create_chat(chat_name=chat_name, creator_id=creator_id)

    def change_chat_name(self, chat_id: str, new_name: str) -> models.Chat:
        """Изменение названия чата"""
        return self._chats_dao.change_chat_name(chat_id=chat_id, new_name=new_name)

    def get_all_chat_members(self) -> list[models.ChatMemberFull]:
        """Получение всех записей таблицы участников чатов"""
        return self._chat_members_dao.get_all_chat_members()

    def get_chat_members(self, chat_id: str) -> list[models.User]:
        """Получение пользователей - участников чата"""
        return self._chat_members_dao.get_chat_members(chat_id=chat_id)

    def find_chat_member(self, user_id: int, chat_id: str) -> tables.ChatMember | None:
        """Поиск участника чата"""
        return self._chat_members_dao.find_chat_member(user_id=user_id, chat_id=chat_id)

    def add_chat_member(self, user_id: int, chat_id: str) -> None:
        """Добавление участника к чату"""
        self._chat_members_dao.add_chat_member(user_id=user_id, chat_id=chat_id)

    def delete_chat_member(self, chat_member: tables.ChatMember) -> None:
        """Удаление участника из чата"""
        self._chat_members_dao.delete_chat_member(chat_member=chat_member)

    def get_all_messages(self) -> list[models.MessageFull]:
        """Получение всех записей из таблицы сообщений"""
        return self._messages_dao.get_all_messages()

    def get_all_read_status_messages(self) -> list[models.MessageReadStatus]:
        """Получение всех записей из таблицы информации о прочтении сообщения пользователем"""
        return self._messages_dao.get_all_read_status_messages()

    def create_text_message(self, text: str, user_id: int, chat_id: str) -> models.Message:
        """Создание текстового сообщения в базе"""
        return self._messages_dao.create_text_message(text=text, user_id=user_id, chat_id=chat_id)

    def create_unread_messages(self, message: models.Message, chat_members: list[models.User]) -> None:
        """Создание записей не прочитанного сообщения для участников чата"""
        self._messages_dao.create_unread_messages(message=message, chat_members=chat_members)

    def mark_message_as_read(self, message_id: str, user_id: int) -> None:
        """Пометить, что пользователь прочитал сообщение"""
        self._messages_dao.mark_message_as_read(message_id=message_id, user_id=user_id)

    def get_unread_message(self, message_id: str, user_id: int) -> tables.MessageReadStatus | None:
        """Получение объекта информации о прочтении сообщения пользователем """
        return self._messages_dao.get_unread_message(message_id=message_id, user_id=user_id)

    def create_info_message(self, text: str, user_id: int, chat_id: str) -> models.Message:
        """Создание информационного сообщения в базе"""
        return self._messages_dao.create_info_message(text=text, user_id=user_id, chat_id=chat_id)

    def get_user_messages(self, user_id: int) -> list[models.ChatData]:
        """Получение сообщений пользователя по всем чатам, где пользователь участник"""
        return self._messages_dao.get_user_messages(user_id=user_id)

    def get_user_chat_messages(self, user_id: int, chat_id: str) -> list[models.ChatData]:
        """Получение сообщений пользователя по конкретному чату"""
        return self._messages_dao.get_user_chat_messages(user_id=user_id, chat_id=chat_id)

    def get_message_by_id(self, message_id: str) -> tables.Message:
        """Получение сообщения по id"""
        return self._messages_dao.get_message_by_id(message_id=message_id)

    def change_message_text(self, message_id: str, new_text: str) -> tables.Message:
        """Изменение текста сообщения"""
        return self._messages_dao.change_message_text(message_id=message_id, new_text=new_text)

    def delete_message(self, message_id: str) -> None:
        """Удаление сообщения из базы"""
        return self._messages_dao.delete_message(message_id=message_id)

    def get_all_contacts(self) -> list[models.ContactFull]:
        """Получение всех записей таблицы контактов из базы"""
        return self._contacts_dao.get_all_contacts()

    def get_user_contacts(self, user_id: int) -> list[models.Contact]:
        """Получение контактов пользователя"""
        return self._contacts_dao.get_user_contacts(user_id=user_id)

    def find_contact(self, owner_user_id: int, contact_user_id: int) -> tables.Contact | None:
        """Нахождение контакта пользователя"""
        return self._contacts_dao.find_contact(owner_user_id=owner_user_id, contact_user_id=contact_user_id)

    def create_contact(self, owner_user_id: int, contact_user_id: int, name: str, surname: str) -> tables.Contact:
        """Создание контакта"""
        return self._contacts_dao.create_contact(owner_user_id=owner_user_id, contact_user_id=contact_user_id, name=name, surname=surname)  # noqa

    def delete_contact(self, contact: tables.Contact) -> None:
        """Удаление контакта"""
        self._contacts_dao.delete_contact(contact=contact)

    def change_contact(self, contact: tables.Contact, new_name: str, new_surname: str) -> None:
        """Изменение данных контакта"""
        self._contacts_dao.change_contact(contact=contact, new_name=new_name, new_surname=new_surname)


def get_db_facade(db_facade: DBFacade = Depends(DBFacade)) -> DBFacadeInterface:
    """Зависимость для получения фасада БД"""
    return db_facade
