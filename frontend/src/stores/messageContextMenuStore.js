import {makeAutoObservable} from 'mobx'
import messagesStore from './messagesStore'


class MessageContextMenuStore {
  messageId = null
  message = null
  messageText = '' // TODO подумать надо ли выделить messageText, showMessageEditModal в отдельный store
  showMessageEditModal = false

  constructor() {
    makeAutoObservable(this)
    console.log("Создан MessageContextMenuStore")
  }

  unsetMessageId() {
    console.log('MessageContextMenuStore unsetMessageId')
    this.messageId = null
    this.message = null
    this.messageText = ''
  }

  // установка id сообщения, вызывается из компонента сообщения при событии contextmenu
  setMessageId(id) {
    console.log('MessageContextMenuStore setMessageId', id)
    this.messageId = id
    this.message = messagesStore.getMessageInCurrentChatById(id)
    this.messageText = this.message.text
  }

  openMessageEditModal() {
    this.showMessageEditModal = true
  }

  closeMessageEditModal() {
    this.showMessageEditModal = false
    this.unsetMessageId()
  }

  setMessageText(text) {
    this.messageText = text
  }

  changeMessageText() {
    this.message.text = this.messageText
  }
}

export default new MessageContextMenuStore()
