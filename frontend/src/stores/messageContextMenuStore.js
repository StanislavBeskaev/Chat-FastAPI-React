import {makeAutoObservable} from 'mobx'
import messagesStore from './messagesStore'
import MessageService from '../services/MessageService'
import confirmDeleteModalStore from './modals/confirmDeleteModalStore'


class MessageContextMenuStore {
  messageId = null
  messageText = ''
  showMessageEditModal = false

  constructor() {
    makeAutoObservable(this)
    console.log("Создан MessageContextMenuStore")
  }

  // установка id сообщения, вызывается из компонента сообщения при событии contextmenu
  setMessageId(id) {
    console.log('MessageContextMenuStore setMessageId', id)
    this.messageId = id
    const message = messagesStore.getMessageInCurrentChatById(id)
    this.messageText = message.text
  }

  unsetMessageId() {
    console.log('MessageContextMenuStore unsetMessageId')
    this.messageId = null
    this.messageText = ''
  }

  async changeMessageText() {
    console.log('Попытка изменения текста сообщения', this.messageId)
    try {
      await MessageService.changeMessageText(this.messageId, this.messageText)
    } catch (e) {
      console.log('Ошибка при изменеении текста сообщения:', e.response)
    }
  }

  openMessageEditModal() {
    this.showMessageEditModal = true
  }

  closeMessageEditModal() {
    this.showMessageEditModal = false
    // что бы при закрытии модалки не показывался пустой текст
    setTimeout(() => {
      this.unsetMessageId()
    }, 400)
  }

  async deleteMessage() {
    console.log('Попытка удалить сообщение', this.messageId, this.messageText)
    try {
      await MessageService.deleteMessage(this.messageId)
    } catch (e) {
      console.log('Ошибка при удалении сообшения', e.response)
    }
  }

  openMessageDeleteModal() {
    confirmDeleteModalStore.open(
      `Вы точно хотите удалить сообщение '${this.messageText}'?`,
      async () => {
        await this.deleteMessage()
        this.unsetMessageId()
      },
      () => {
        this.unsetMessageId()
      }
    )
  }

  setMessageText(text) {
    this.messageText = text
  }
}

export default new MessageContextMenuStore()
