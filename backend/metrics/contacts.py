from backend.metrics import RequestCounter

GET_CONTACTS_COUNTER = RequestCounter("get_contacts", "Количество запросов на получение списка контактов")
CREATE_CONTACT_COUNTER = RequestCounter("create_contact", "Количество запросов на создание контактов")
DELETE_CONTACT_COUNTER = RequestCounter("delete_contact", "Количество запросов на удаление контактов")
GET_CONTACT_INFO_COUNTER = RequestCounter("get_contact_info", "Количество запросов на получение данных контакта")
CHANGE_CONTACT_COUNTER = RequestCounter("change_contact", "Количество запросов на изменение контактов")
