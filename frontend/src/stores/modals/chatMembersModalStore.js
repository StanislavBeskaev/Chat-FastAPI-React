import {makeAutoObservable} from "mobx"

import MessageService from '../../services/MessageService'


class ChatMembersModalStore {
  show = false
  chatId = null
  error = ''
  members = []
  message = ''
  messageCloseTimeout = null

  constructor() {
    makeAutoObservable(this)
    console.log("ChatMembersModalStore NewChatModalStore")
  }

  async openWithChatId(chatId) {
    this.chatId = chatId
    this.error = ''
    if (this.messageCloseTimeout) clearTimeout(this.messageCloseTimeout)
    await this.loadChatMembers()
    this.setShow(true)
  }

  async loadChatMembers() {
    try {
      console.log('Запрос участников чата', this.chatId)
      const response = await MessageService.getChatMembers(this.chatId)
      this.setMembers(response.data)
      console.log(response)
    } catch (e) {
      console.log('Ошибка при загрузке участников чата', this.chatId)
      console.log(e.response)
    }
  }

  async addChatMember(login) {
    try {
      console.log(`Попытка добавить пользователя ${login} к чату ${this.chatId}`)
      await MessageService.addChatMember(this.chatId, login)
      console.log('Пользователь добавлен к чату')
      await this.loadChatMembers()
      this.addMessage(`Пользователь ${login} добавлен к чату`)
    } catch (e) {
      console.log('Ошибка при добавлении пользователя к чату')
      console.log(e.response)
      if (e.response.status === 409) {
        await this.loadChatMembers()
        this.addMessage("Этот пользователь уже добавлен")
      }
    }
  }

  async deleteChatMember(login) {
    try {
      console.log(`Попытка удалить пользователя ${login} из чата:${this.chatId}`)
      await MessageService.deleteChatMember(this.chatId, login)
      console.log('Пользователь удалён из чата')
      await this.loadChatMembers()
      this.addMessage(`Пользователь ${login} удалён из чата`)
    } catch (e) {
      console.log('Ошибка при удалении пользователя из чата')
      console.log(e.response)
      if (e.response.status === 404) {
        await this.loadChatMembers()
        this.addMessage("Этот пользователь уже удалён из чата")
      }
    }
  }

  addMessage(message) {
    this.setMessage(message)
    if (this.messageCloseTimeout) clearTimeout(this.messageCloseTimeout)
    this.messageCloseTimeout = setTimeout(() => {
      this.setMessage('')
    }, 2000)
  }

  close() {
    this.show = false
  }

  setError(text) {
    this.error = text
  }

  setShow(bool) {
    this.show = bool
  }

  setMembers(data) {
    this.members = data
  }

  setMessage(text) {
    this.message = text
  }
}

export default new ChatMembersModalStore()
