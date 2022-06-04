import {makeAutoObservable} from "mobx"

import ContactService from '../../services/ContactService'


class ContactModalStore {
  show = false
  login = null
  loading = false
  contactInfo = null

  constructor() {
    makeAutoObservable(this)
    console.log("Создан ContactModalStore")
  }

  close() {
    this.show = false
  }

  async showWithLogin(login) {
    this.login = login
    this.show = true
    await this.loadContactInfo()
  }

  async loadContactInfo() {
    this.setLoading(true)
    try {
      this.contactInfo = await ContactService.getOne(this.login)
    } catch (e) {
      console.log(`Ошибка при загрузке данных контакта: ${this.login}`, e)
    } finally {
      this.setLoading(false)
    }
  }

  setLoading(bool) {
    this.loading = bool
  }
}

export default new ContactModalStore()
