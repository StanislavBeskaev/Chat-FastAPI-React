from backend.metrics import RequestCounter


GET_CONTACTS_CNT = RequestCounter("get_contacts", "Количество запросов на получение списка контактов")
CREATE_CONTACT_CNT = RequestCounter("create_contact", "Количество запросов на создание контактов")
DELETE_CONTACT_CNT = RequestCounter("delete_contact", "Количество запросов на удаление контактов")
GET_CONTACT_INFO_CNT = RequestCounter("get_contact_info", "Количество запросов на получение данных контакта")
CHANGE_CONTACT_CNT = RequestCounter("change_contact", "Количество запросов на изменение контактов")
