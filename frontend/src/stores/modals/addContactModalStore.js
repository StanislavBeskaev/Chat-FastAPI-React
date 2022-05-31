import {makeAutoObservable} from "mobx"

import UserService from '../../services/UserService'


class AddContactModalStore {
  show = false
  login = null
  userInfo = null
  loadError = false

  constructor() {
    makeAutoObservable(this)
    console.log("Создан MessagesStore")
  }

  async loadUserInfo() {
    try {
      const data = await UserService.getUserInfo(this.login)
      this.setLoadError(false)
      this.setUserInfo(data)
    } catch (e) {
      console.log(`Ошибка при загрузке данных пользователя: ${this.login}`)
      this.setLoadError(true)
    }
  }

  setShow(bool) {
    this.show = bool
  }

  setLogin(login) {
    this.login = login
  }

  setUserInfo(data) {
    this.userInfo = data
  }

  setLoadError(bool) {
    this.loadError = bool
  }
}

export default new AddContactModalStore()
