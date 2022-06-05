import {makeAutoObservable} from "mobx"

import UserService from '../../services/UserService'
import contactStore from '../contactStore'
import ContactService from '../../services/ContactService'


class AddContactModalStore {
  show = false
  login = null
  userInfo = null
  error = null
  successAdd = false
  loading = false
  closeTimeout = null

  constructor() {
    makeAutoObservable(this)
    console.log("Создан AddContactModalStore")
  }

  async showModalWithLogin(login) {
    this.login = login
    this.show = true
    this.userInfo = null
    this.error = null
    this.successAdd = false
    if (this.closeTimeout) clearTimeout(this.closeTimeout)
    await this.loadUserInfo()
  }

  close() {
    this.show = false
  }

  async loadUserInfo() {
    this.setLoading(true)
    try {
      const data = await UserService.getUserInfo(this.login)
      this.setUserInfo(data)
    } catch (e) {
      console.log(`Ошибка при загрузке данных пользователя: ${this.login}`)
    } finally {
      this.setLoading(false)
    }
  }

  async handleAddContact() {
    if (!this.login) {
      console.log("Попытка добавить пустой контакт")
      this.error = "Попытка добавить пустой контакт"
      return
    }

    this.error = null
    console.log("Пробуем добавить новый контакт:", this.login)
    try {
      const response = await ContactService.createContact(this.login)
      console.log("handleAddContact response", response)
      contactStore.addContact(response.data)

      this.setSuccessAdd(true)
      this.closeTimeout = setTimeout(() => {
        this.close()
      }, 2000)
    } catch (e) {
      console.log("Возникла ошибка при добавлении контакта", e)
      this.error = e.response.data.detail
    }
  }

  setUserInfo(data) {
    this.userInfo = data
  }

  setError(error) {
    this.error = error
  }

  setLoading(bool) {
    this.loading = bool
  }

  setSuccessAdd(bool) {
    this.successAdd = bool
  }
}

export default new AddContactModalStore()
