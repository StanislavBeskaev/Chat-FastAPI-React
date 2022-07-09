import {makeAutoObservable} from 'mobx'

import authStore from './authStore'
import MessageService from '../services/MessageService'


const DEFAULT_CHAT_ID = 'MAIN'

class MessagesStore {
  chats = {}
  selectedChatId = DEFAULT_CHAT_ID
  isLoadMessages = false
  loading = false
  loadError = false
  selectedChatText = ''
  selectedChatTyping = false

  constructor() {
    makeAutoObservable(this)
    console.log("Создан MessagesStore")
  }

  setDefaultState() {
    this.chats = {}
    this.selectedChatId = DEFAULT_CHAT_ID
    this.isLoadMessages = false
    this.loading = false
    this.loadError = false
    this.selectedChatText = ''
    this.selectedChatTyping = false
  }

  addNewChat(data) {
    const {chat_id: chatId, chat_name: chatName, creator} = data
    this.chats[chatId] = {
      "chat_name": chatName,
      messages: [],
      typingLogins: [],
      text: '',
      creator
    }
    console.log(`Добавлен новый чат: ${chatName}`)
  }

  getChatUnreadMessagesCount(chatId) {
    const chatUnreadMessages = this.chats[chatId].messages.filter(message => message.is_read === false)
    return chatUnreadMessages.length
  }

  changeChatName(data) {
    const {chat_id: chatId, chat_name: chatName} = data
    this.chats[chatId]["chat_name"] = chatName
    console.log(`Изменено название чата ${chatId} на ${chatName}`)
  }

  getChatNameById(chatId) {
    return this.chats[chatId]?.chat_name
  }

  getSelectedChatName() {
    return this.getChatNameById(this.selectedChatId)
  }

  getSelectedChatCreator() {
    return this.getChatCreator(this.selectedChatId)
  }

  getChatCreator(chatId) {
    return this.chats[chatId]?.creator
  }

  async loadMessages() {
    console.log("load messages")
    this.setLoading(true)
    try{
      const response = await MessageService.getMessages()
      console.log("success load, response:", response)
      this.setChats(response.data)
      this.setLoadError(false)
      this.setIsLoadMessages(true)
    } catch (e) {
      console.log("Ошибка при зарузке сообщений:", e)
      this.setLoadError(true)
    } finally {
      this.setLoading(false)
    }
  }

  deleteChat(chatId) {
    console.log('Попытка удаления чата', chatId)
    if (this.selectedChatId === chatId) {
      this.setSelectedChatId(DEFAULT_CHAT_ID)
    }
    delete this.chats[chatId]
    console.log('Удалён чат', chatId)
  }

  async addChat(chatId) {
    console.log('Попытка добавления чата', chatId)
    try{
      console.log(`Запрос данных чата`, chatId)
      const response = await MessageService.getChatMessages(chatId)
      console.log(response)
      this.chats[chatId] = response.data
      // TODO подумать как сделать красиво initChat
      this.initChat(chatId)
    } catch (e) {
      console.log('Ошибка при загрузке данных чата', chatId)
      console.log(e.response)
    }
    console.log('Чат добавлен', chatId)
  }

  addMessage(message) {
    if (!this.isLoadMessages) return

    const {chat_id: chatId} = message
    console.log(`MessagesStore add message to chatId "${chatId}":`, message)
    this.chats[chatId].messages.push(message)
  }

  markMessageAsRead(messageId, chatId) {
    console.log(`Помечаем прочитанным сообщение ${messageId} из чата ${chatId}`)
    for (let message of this.chats[chatId].messages) {
      if (message.message_id === messageId) {
        message.is_read = true
        console.log(`Сообщение ${messageId} помечено прочитанным`)
      }
    }
  }

  addTypingLogin(chatId, login) {
    if (login === authStore.user.login) return

    this.chats[chatId].typingLogins = Array.from(new Set([...this.chats[chatId].typingLogins, login]))
  }

  deleteTypingLogin(chatId, login) {
    if (login === authStore.user.login) return

    this.chats[chatId].typingLogins = this.chats[chatId].typingLogins.filter(typingLogin => typingLogin !== login)
  }

  selectedChatMessages() {
    return this.chats[this.selectedChatId].messages
  }

  selectedChatTypingLogins() {
    return this.chats[this.selectedChatId].typingLogins
  }

  setSelectedChatText(text) {
    this.chats[this.selectedChatId].text = text
    this.selectedChatText = text
  }

  setSelectedChatTyping(bool) {
    this.selectedChatTyping = bool
  }
  
  setChats(chats) {
    this.chats = chats
    for (let chatId of Object.keys(this.chats)) {
      this.initChat(chatId)
    }
  }

  // Инициализация чата, добавление служебных полей
  initChat(chatId) {
    this.chats[chatId].typingLogins = []
    this.chats[chatId].text = ''
  }

  setSelectedChatId(chatId) {
    this.selectedChatId = chatId
    this.selectedChatText = this.chats[chatId].text
    this.selectedChatTyping = false
  }

  setIsLoadMessages(bool) {
    this.isLoadMessages = bool
  }

  setLoading(bool) {
    this.loading = bool
  }

  setLoadError(bool) {
    this.loadError = bool
  }
}

export default new MessagesStore()
