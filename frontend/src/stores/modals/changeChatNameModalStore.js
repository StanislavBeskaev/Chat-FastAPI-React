import {makeAutoObservable} from "mobx"
import messagesStore from '../messagesStore'
import ChatService from "../../services/ChatService"
import logMessages from '../../log'


class ChangeChatNameModalStore {
  show = false
  name = ''
  previousName = ''
  chatId = null
  error = ''
  success = false
  closeTimeout = null

  constructor() {
    makeAutoObservable(this)
    logMessages("Создан NewChatModalStore")
  }


  openWithChatId(chatId) {
    this.chatId = chatId
    this.name = messagesStore.getChatNameById(chatId)
    this.previousName = messagesStore.getChatNameById(chatId)
    this.error = ''
    this.success = false
    if (this.closeTimeout) clearTimeout(this.closeTimeout)
    this.show = true
  }

  async changeChatName() {
    logMessages("Попытка изменения названия чата")
    try {
      await ChatService.changeChatName(this.chatId, this.name)
      this.setSuccess(true)
      this.setError('')

      this.closeTimeout = setTimeout(() => {
        this.close()
      }, 2000)
    } catch (e) {
      logMessages('Ошибка при изменении названия чата')
      logMessages(e.response)
      this.setError(e.response.data.detail)
    }
  }

  close() {
    this.show = false
  }

  setName(value) {
    this.name = value
    if (this.error) this.setError('')
  }

  setSuccess(bool) {
    this.success = bool
  }

  setError(text) {
    this.error = text
  }
}

export default new ChangeChatNameModalStore()
