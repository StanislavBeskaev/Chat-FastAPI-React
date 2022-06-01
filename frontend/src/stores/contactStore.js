import {makeAutoObservable} from "mobx"

import ContactService from '../services/ContactService'
import addContactModalStore from './modals/addContactModalStore'


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

  async addContact(login) {
    console.log("Пробуем добавить новый контакт:", login)
    this.setLoading(true)
    try {
      const response = await ContactService.createContact(login)
      console.log("addContact response", response)
      this.contacts.push(response.data)
      //TODO перенести ошибку в addContactModalStore и оттуда сделать вызов addContact
      addContactModalStore.setShow(false)
    } catch (e) {
      console.log("Возникла ошибка при добавлении контакта", e)
      this.setError(e.response.data.detail)
    } finally {
      this.setLoading(false)
    }
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
