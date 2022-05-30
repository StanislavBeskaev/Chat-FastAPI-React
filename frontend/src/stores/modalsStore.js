import {makeAutoObservable} from "mobx"
import UserService from '../services/UserService'


class ModalsStore {
  showAddContact = false
  addContactLogin = null
  addContactUserInfo = null

  constructor() {
    makeAutoObservable(this)
    console.log("Создан MessagesStore")
  }

  async loadUserInfo() {
    const data = await UserService.getUserInfo(this.addContactLogin)
    this.setAddConcatUserInfo(data)
  }

  setShowAddContact(bool) {
    this.showAddContact = bool
  }

  setAddContactLogin(login) {
    this.addContactLogin = login
  }

  setAddConcatUserInfo(data) {
    this.addContactUserInfo = data
  }
}

export default new ModalsStore()
