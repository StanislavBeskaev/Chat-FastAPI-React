import {makeAutoObservable} from "mobx"

import authStore from '../authStore'
import ChatService from "../../services/ChatService"


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
      await ChatService.createNewChat(this.name, this.logins)
      this.setSuccess(true)
      this.setError('')

      this.closeTimeout = setTimeout(() => {
        this.close()
      }, 2000)
    } catch (e) {
      const error = e
      console.log('Ошибка при создании нового чата')
      console.log(error.response)
      this.setError(error.response.data.detail)
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
