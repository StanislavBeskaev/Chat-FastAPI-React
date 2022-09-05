import {makeAutoObservable} from "mobx"

import ContactService from '../../services/ContactService'
import contactStore from '../contactStore'
import logMessages from '../../log'


class ContactModalStore {
  show = false
  login = null
  name = null
  surname = null
  loading = false
  changed = false

  constructor() {
    makeAutoObservable(this)
    logMessages("Создан ContactModalStore")
  }

  close() {
    this.show = false
  }

  async showWithLogin(login) {
    this.login = login
    this.changed = false
    this.show = true
    await this.loadContactInfo()
  }

  async loadContactInfo() {
    this.setLoading(true)
    try {
      logMessages(`Загружаем информацию о контакте ${this.login}`)
      const response = await ContactService.getOne(this.login)
      logMessages(response)
      this.setName(response.data.name)
      this.setSurname(response.data.surname)
    } catch (e) {
      logMessages(`Ошибка при загрузке данных контакта: ${this.login}`, e)
    } finally {
      this.setLoading(false)
    }
  }

  async changeContact() {
    logMessages(`Пробуем изменить контакт ${this.login}, имя=${this.name}, фамилия=${this.surname}`)
    try {
      const response = await ContactService.changeContact(this.login, this.name, this.surname)
      await contactStore.loadContacts()
      this.setChanged(true)
      logMessages(response)
    } catch (e) {
      logMessages(`Ошибка при изменении контакт ${this.login}`, e)
    }
  }

  setLoading(bool) {
    this.loading = bool
  }

  setName(name) {
    this.name = name
    this.changed = false
  }

  setSurname(surname) {
    this.surname = surname
    this.changed = false
  }

  setChanged(bool) {
    this.changed = bool
  }
}

export default new ContactModalStore()
