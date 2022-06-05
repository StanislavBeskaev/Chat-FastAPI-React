import {makeAutoObservable} from "mobx"


class ConfirmDeleteContactModalStore {
  show = false
  login = null

  constructor() {
    makeAutoObservable(this)
    console.log("Создан ConfirmDeleteContactModalStore")
  }

  showWithLogin(login) {
    this.login = login
    this.show = true
  }

  close() {
    this.show = false
  }

  setShow(bool) {
    this.show = bool
  }
}

export default new ConfirmDeleteContactModalStore()
