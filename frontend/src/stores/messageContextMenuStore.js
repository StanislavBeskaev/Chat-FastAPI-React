import {makeAutoObservable} from 'mobx'
import messagesStore from './messagesStore'
import MessageService from '../services/MessageService'
import confirmDeleteModalStore from './modals/confirmDeleteModalStore'
import logMessages from '../log'


class MessageContextMenuStore {
  messageId = null
  messageText = ''
  beforeChangeMessageText = ''
  showMessageEditModal = false

  constructor() {
    makeAutoObservable(this)
    logMessages("Создан MessageContextMenuStore")
  }

  // установка id сообщения, вызывается из компонента сообщения при событии contextmenu
  setMessageId(id) {
    logMessages('MessageContextMenuStore setMessageId', id)
    this.messageId = id
    const message = messagesStore.getMessageInCurrentChatById(id)
    this.messageText = message.text
    this.beforeChangeMessageText = message.text
  }

  unsetMessageId() {
    logMessages('MessageContextMenuStore unsetMessageId')
    this.messageId = null
    this.messageText = ''
    this.beforeChangeMessageText = ''
  }

  async changeMessageText() {
    logMessages('Попытка изменения текста сообщения', this.messageId)
    try {
      await MessageService.changeMessageText(this.messageId, this.messageText)
      this.closeMessageEditModal()
    } catch (e) {
      logMessages('Ошибка при изменении текста сообщения:', e.response)
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
    logMessages('Попытка удалить сообщение', this.messageId, this.messageText)
    try {
      await MessageService.deleteMessage(this.messageId)
    } catch (e) {
      logMessages('Ошибка при удалении сообшения', e.response)
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
