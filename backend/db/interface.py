from abc import ABC, abstractmethod

from backend import models, tables


class DBFacadeInterface(ABC):
    """Интерфейс фасада базы данных"""

    @abstractmethod
    def get_all_users(self) -> list[models.User]:
        """Получение всех записей таблицы пользователей"""
        ...

    @abstractmethod
    def get_all_profiles(self) -> list[models.Profile]:
        """Получение всех записей таблицы профилей"""
        ...

    @abstractmethod
    def create_user(self, login: str, password_hash: str, name: str, surname: str) -> models.User:
        """Создание пользователя"""
        ...

    @abstractmethod
    def create_user_profile(self, user_id) -> None:
        """Создание профиля для пользователя"""
        ...

    @abstractmethod
    def find_user_by_login(self, login: str) -> tables.User | None:
        """Поиск пользователя по login"""
        ...

    @abstractmethod
    def find_user_by_id(self, user_id: int) -> tables.User | None:
        """Поиск пользователя по id"""
        ...

    @abstractmethod
    def get_user_info(self, login: str) -> models.User:
        """Получение информации и пользователе"""
        ...

    @abstractmethod
    def change_user_data(self, login: str, name: str, surname: str) -> models.User:
        """Изменение данных пользователя"""
        ...

    @abstractmethod
    def get_profile_by_login(self, login: str) -> models.Profile:
        """Нахождение профайла пользователя по логину пользователя"""
        ...

    @abstractmethod
    def set_avatar_file(self, user_id: int, avatar_file: str) -> None:
        """Установка имени файла аватара для пользователя"""
        ...

    @abstractmethod
    def get_used_avatar_files(self) -> list[str]:
        """Получение названий используемых файлов аватаров"""
        ...

    @abstractmethod
    def get_all_refresh_tokens(self) -> list[models.RefreshToken]:
        """Получение всех записей таблицы refresh токенов"""
        ...

    @abstractmethod
    def find_refresh_token_by_user(self, user_id: int, user_agent: str) -> tables.RefreshToken | None:
        """Поиск refresh токена по пользователю и user_agent"""
        ...

    @abstractmethod
    def find_refresh_token_by_token(self, token: str, user_agent: str) -> tables.RefreshToken | None:
        """Поиск refresh токена по токену и user_agent"""
        ...

    @abstractmethod
    def create_refresh_token(self, user_id: int, refresh_token: str, user_agent: str) -> tables.RefreshToken:
        """Создание refresh токена"""
        ...

    @abstractmethod
    def update_refresh_token(self, token: tables.RefreshToken, new_refresh_token: str) -> tables.RefreshToken:
        """Обновление refresh токена"""
        ...

    @abstractmethod
    def delete_refresh_token(self, token: str, user_agent: str) -> None:
        """Удаление refresh токена"""
        ...

    @abstractmethod
    def get_all_chats(self) -> list[models.Chat]:
        """Получение всех записей из таблицы чатов"""
        ...

    @abstractmethod
    def get_chat_by_id(self, chat_id: str) -> models.Chat:
        """Получение чата по id"""
        ...

    @abstractmethod
    def create_chat(self, chat_name: str, creator_id: int) -> models.Chat:
        """Создание нового чата"""
        ...

    @abstractmethod
    def change_chat_name(self, chat_id: str, new_name: str) -> models.Chat:
        """Изменение названия чата"""
        ...

    @abstractmethod
    def delete_chat(self, chat_id) -> None:
        """Удаление чата"""
        ...

    @abstractmethod
    def get_all_chat_members(self) -> list[models.ChatMemberFull]:
        """Получение всех записей таблицы участников чатов"""
        ...

    @abstractmethod
    def get_chat_members(self, chat_id: str) -> list[models.User]:
        """Получение пользователей - участников чата"""
        ...

    @abstractmethod
    def find_chat_member(self, user_id: int, chat_id: str) -> tables.ChatMember | None:
        """Поиск участника чата"""
        ...

    @abstractmethod
    def add_chat_member(self, user_id: int, chat_id: str) -> None:
        """Добавление участника к чату"""
        ...

    @abstractmethod
    def delete_chat_member(self, chat_member: tables.ChatMember) -> None:
        """Удаление участника из чата"""
        ...

    @abstractmethod
    def get_all_messages(self) -> list[models.MessageFull]:
        """Получение всех записей из таблицы сообщений"""
        ...

    @abstractmethod
    def get_all_read_status_messages(self) -> list[models.MessageReadStatus]:
        """Получение всех записей из таблицы информации о прочтении сообщения пользователем"""
        ...

    @abstractmethod
    def create_text_message(self, text: str, user_id: int, chat_id: str) -> models.Message:
        """Создание текстового сообщения в базе"""
        ...

    @abstractmethod
    def create_unread_messages(self, message: models.Message, chat_members: list[models.User]) -> None:
        """Создание записей не прочитанного сообщения для участников чата"""
        ...

    @abstractmethod
    def mark_message_as_read(self, message_id: str, user_id: int) -> None:
        """Пометить, что пользователь прочитал сообщение"""
        ...

    @abstractmethod
    def get_unread_message(self, message_id: str, user_id: int) -> tables.MessageReadStatus | None:
        """Получение объекта информации о прочтении сообщения пользователем"""
        ...

    @abstractmethod
    def create_info_message(self, text: str, user_id: int, chat_id: str) -> models.Message:
        """Создание информационного сообщения в базе"""
        ...

    @abstractmethod
    def get_user_messages(self, user_id: int) -> list[models.ChatData]:
        """Получение сообщений пользователя по всем чатам, где пользователь участник"""
        ...

    @abstractmethod
    def get_user_chat_messages(self, user_id: int, chat_id: str) -> list[models.ChatData]:
        """Получение сообщений пользователя по конкретному чату"""
        ...

    @abstractmethod
    def get_message_by_id(self, message_id: str) -> tables.Message:
        """Получение сообщения по id"""
        ...

    @abstractmethod
    def change_message_text(self, message_id: str, new_text: str) -> tables.Message:
        """Изменение текста сообщения"""
        ...

    @abstractmethod
    def delete_message(self, message_id: str) -> None:
        """Удаление сообщения из базы"""
        ...

    @abstractmethod
    def get_all_contacts(self) -> list[models.ContactFull]:
        """Получение всех записей таблицы контактов из базы"""
        ...

    @abstractmethod
    def get_user_contacts(self, user_id: int) -> list[models.Contact]:
        """Получение контактов пользователя"""
        ...

    @abstractmethod
    def find_contact(self, owner_user_id: int, contact_user_id: int) -> tables.Contact | None:
        """Нахождение контакта пользователя"""
        ...

    @abstractmethod
    def create_contact(self, owner_user_id: int, contact_user_id: int, name: str, surname: str) -> tables.Contact:
        """Создание контакта"""
        ...

    @abstractmethod
    def delete_contact(self, contact: tables.Contact) -> None:
        """Удаление контакта"""
        ...

    @abstractmethod
    def change_contact(self, contact: tables.Contact, new_name: str, new_surname: str) -> None:
        """Изменение данных контакта"""
        ...
