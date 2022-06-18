import {makeAutoObservable} from "mobx"

import MessageService from '../../services/MessageService'
import authStore from '../authStore'


class NewChatModalStore {
  show = false
  name = ''
  logins = []
  error = ''
  success = false
  closeTimeout = null

  constructor() {
    makeAutoObservable(this)
    console.log("Создан NewChatModalStore")
  }

  async createNewChat() {
    console.log("Попытка создания нового чата")
    try {
      await MessageService.createNewChat(this.name, this.logins)
      this.setSuccess(true)
      this.setError('')

      this.closeTimeout = setTimeout(() => {
        this.close()
      }, 2000)
    } catch (e) {
      const errorText = JSON.stringify(e?.response?.data?.detail)
      console.log(errorText)
      // TODO убрать двойные ковычки вокруг текста ошибки везде где подобное
      this.setError(errorText)
    }
  }

  open() {
    this.name = ''
    this.logins = [authStore.user.login]
    this.error = ''
    this.success = false
    if (this.closeTimeout) clearTimeout(this.closeTimeout)
    this.show = true
  }

  close() {
    this.show = false
  }

  setName(value) {
    this.name = value
  }

  toggleLogin(value) {
    if (this.logins.includes(value)) {
      this.logins = this.logins.filter(login => login !== value)
    } else {
      this.logins.push(value)
    }
  }

  setSuccess(bool) {
    this.success = bool
  }

  setError(text) {
    this.error = text
  }
}

export default new NewChatModalStore()
