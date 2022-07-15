import {makeAutoObservable} from "mobx"
import messagesStore from '../messagesStore'
import ChatService from "../../services/ChatService"


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
    console.log("Создан NewChatModalStore")
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
    console.log("Попытка изменения названия чата")
    try {
      await ChatService.changeChatName(this.chatId, this.name)
      this.setSuccess(true)
      this.setError('')

      this.closeTimeout = setTimeout(() => {
        this.close()
      }, 2000)
    } catch (e) {
      console.log('Ошибка при изменении названия чата чата')
      console.log(e.response)
      this.setError(e.response.data.detail)
    }
  }

  close() {
    this.show = false
  }

  setName(value) {
    this.name = value
  }

  setSuccess(bool) {
    this.success = bool
  }

  setError(text) {
    this.error = text
  }
}

export default new ChangeChatNameModalStore()
