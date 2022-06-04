import {makeAutoObservable} from "mobx"

import ContactService from '../../services/ContactService'
import contactStore from '../contactStore'


class ContactModalStore {
  show = false
  login = null
  name = null
  surname = null
  avatarFile = null
  loading = false
  changed = false

  constructor() {
    makeAutoObservable(this)
    console.log("Создан ContactModalStore")
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
      console.log(`Загружаем информацию о контакте ${this.login}`)
      const response = await ContactService.getOne(this.login)
      console.log(response)
      this.setName(response.data.name)
      this.setSurname(response.data.surname)
      this.setAvatarFile(response.data.avatar_file)
    } catch (e) {
      console.log(`Ошибка при загрузке данных контакта: ${this.login}`, e)
    } finally {
      this.setLoading(false)
    }
  }

  async changeContact() {
    console.log(`Пробуем изменить контакт ${this.login}, имя=${this.name}, фамилия=${this.surname}`)
    try {
      const response = await ContactService.changeContact(this.login, this.name, this.surname)
      await contactStore.loadContacts()
      this.setChanged(true)
      console.log(response)
    } catch (e) {
      console.log(`Ошибка при изменении контакт ${this.login}`, e)
    }
  }

  setLoading(bool) {
    this.loading = bool
  }

  setName(name) {
    this.name = name
  }

  setSurname(surname) {
    this.surname = surname
  }

  setAvatarFile(avatarFile) {
    this.avatarFile = avatarFile
  }

  setChanged(bool) {
    this.changed = bool
  }
}

export default new ContactModalStore()
