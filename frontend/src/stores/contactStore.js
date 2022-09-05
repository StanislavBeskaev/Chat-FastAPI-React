import {makeAutoObservable} from 'mobx'

import ContactService from '../services/ContactService'
import logMessages from '../log'


class ContactStore {
  contacts = []
  loading = false
  error = null

  constructor() {
    makeAutoObservable(this)
    logMessages("Создан ContactStore")
  }

  async loadContacts() {
    logMessages("Загружаем контакты")
    this.setLoading(true)
    try {
      const response = await ContactService.getContacts()
      logMessages("loadContacts response", response)
      this.setContacts(response.data)
    } catch (e) {
      logMessages("Возникла ошибка при загрузке контактов", e)
    } finally {
      this.setLoading(false)
    }
  }

   addContact(contact) {
    this.contacts.push(contact)
    logMessages("ContactStore, добавлен новый контакт:", contact)
  }

  async deleteContact(login) {
    logMessages("Попытка удалить контакт:", login)
    try {
      await ContactService.deleteContact(login)
      this.setContacts(this.contacts.filter(contact => contact.login !== login))
      logMessages("Удалён контакт ", login)
    } catch (e) {
      logMessages(`Не удалось удалить контакт ${login}`, e)
    }
  }

  hasLogin(login) {
    const loginContact = this.findContactByLogin(login)

    return !!loginContact
  }

  findContactByLogin(login) {
    return this.contacts.find(contact => contact.login === login)
  }

  getDisplayName(login) {
    const loginContact = this.findContactByLogin(login)
    if (!loginContact) {
      return login
    }

    const {name, surname} = loginContact
    let displayName

    if (name && surname) {
      displayName = `(${name} ${surname})`
    } else if (name && !surname) {
      displayName = `(${name})`
    } else if (!name && surname) {
      displayName = `(${surname})`
    } else {
      displayName = ''
    }

    return `${login} ${displayName}`
  }

  setLoading(bool) {
    this.loading = bool
  }

  setContacts(data) {
    this.contacts = data
  }

  setError(error) {
    logMessages("ContactStore setError", error)
    this.error = error
  }
}

export default new ContactStore()
