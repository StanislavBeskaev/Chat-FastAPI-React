import {makeAutoObservable} from "mobx"

import MessageService from '../../services/MessageService'


class ChatMembersModalStore {
  show = false
  chatId = null
  error = ''
  members = []
  closeTimeout = null

  constructor() {
    makeAutoObservable(this)
    console.log("ChatMembersModalStore NewChatModalStore")
  }

  async openWithChatId(chatId) {
    this.chatId = chatId
    this.error = ''
    if (this.closeTimeout) clearTimeout(this.closeTimeout)
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
      // TODO оповещение о добавлении пользователя к чату
      console.log("Пользователь добавлен к чату")
      await this.loadChatMembers()
    } catch (e) {
      console.log('Ошибка при добавлении пользователя к чату')
      console.log(e.response)
    }
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
}

export default new ChatMembersModalStore()
