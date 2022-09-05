import {makeAutoObservable} from "mobx"

import ChatMembersService from "../../services/chatMembersService"
import logMessages from '../../log'


class ChatMembersModalStore {
  show = false
  chatId = null
  error = ''
  members = []
  message = ''
  messageCloseTimeout = null

  constructor() {
    makeAutoObservable(this)
    logMessages("ChatMembersModalStore NewChatModalStore")
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
      logMessages('Запрос участников чата', this.chatId)
      const response = await ChatMembersService.getChatMembers(this.chatId)
      this.setMembers(response.data)
      logMessages(response)
    } catch (e) {
      logMessages('Ошибка при загрузке участников чата', this.chatId)
      logMessages(e.response)
    }
  }

  async addChatMember(login) {
    try {
      logMessages(`Попытка добавить пользователя ${login} к чату ${this.chatId}`)
      await ChatMembersService.addChatMember(this.chatId, login)
      logMessages('Пользователь добавлен к чату')
      await this.loadChatMembers()
      this.addMessage(`Пользователь ${login} добавлен к чату`)
    } catch (e) {
      logMessages('Ошибка при добавлении пользователя к чату')
      logMessages(e.response)
      if (e.response.status === 409) {
        await this.loadChatMembers()
        this.addMessage("Этот пользователь уже добавлен")
      }
    }
  }

  async deleteChatMember(login) {
    try {
      logMessages(`Попытка удалить пользователя ${login} из чата:${this.chatId}`)
      await ChatMembersService.deleteChatMember(this.chatId, login)
      logMessages('Пользователь удалён из чата')
      await this.loadChatMembers()
      this.addMessage(`Пользователь ${login} удалён из чата`)
    } catch (e) {
      logMessages('Ошибка при удалении пользователя из чата')
      logMessages(e.response)
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
    logMessages('Закрываем модальное окно с участниками чата')
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
