import {makeAutoObservable} from "mobx"

import ContactService from '../services/ContactService'


class ContactStore {
  contacts = []
  loading = false
  error = null

  constructor() {
    makeAutoObservable(this)
    console.log("Создан ContactStore")
  }

  async loadContacts() {
    console.log("Загружаем контакты")
    this.setLoading(true)
    try {
      const response = await ContactService.getContacts()
      console.log("loadContacts response", response)
      this.setContacts(response.data)
    } catch (e) {
      console.log("Возникла ошибка при загрузке контактов", e)
    } finally {
      this.setLoading(false)
    }
  }

   addContact(contact) {
    this.contacts.push(contact)
    console.log("ContactStore, добавлен новый контакт:", contact)
  }

  async deleteContact(login) {
    console.log("Попытка удалить контакт:", login)
    try {
      await ContactService.deleteContact(login)
      this.setContacts(this.contacts.filter(contact => contact.login !== login))
      console.log("Удалён контакт ", login)
    } catch (e) {
      console.log(`Не удалось удалить контакт ${login}`, e)
    }
  }

  hasLogin(login) {
    const loginContact = this.contacts.find(contact => contact.login === login)

    return !!loginContact
  }

  setLoading(bool) {
    this.loading = bool
  }

  setContacts(data) {
    this.contacts = data
  }

  setError(error) {
    console.log("ContactStore setError", error)
    this.error = error
  }
}

export default new ContactStore()
