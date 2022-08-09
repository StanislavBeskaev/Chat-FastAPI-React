import {makeAutoObservable} from 'mobx'

import authStore from './authStore'
import MessageService from '../services/MessageService'
import searchMessagesStore from './searchMessagesStore'


const DEFAULT_CHAT_ID = 'MAIN'

class MessagesStore {
  chats = {}
  selectedChatId = DEFAULT_CHAT_ID
  isLoadMessages = false
  loading = false
  loadError = false
  selectedChatText = ''
  selectedChatTyping = false
  waitReadList = []
  needScrollToNewMessage = false

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
    this.waitReadList = []
    this.needScrollToNewMessage = false

    searchMessagesStore.setDefaultState()
  }

  // Первоначальная загрузка информации о сообщениях, выделение чатов
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

  setChats(chats) {
    this.chats = chats
    const chatIds = Object.keys(this.chats)
    for (let chatId of chatIds) {
      this.initChat(chatId)
    }

    searchMessagesStore.initialize(chatIds)
  }

  // Инициализация чата, добавление служебных полей
  initChat(chatId) {
    this.chats[chatId].typingLogins = []
    this.chats[chatId].text = ''
    this.chats[chatId].messagesInView = []
    this.chats[chatId].wasOpened = false
    for (let message of this.chats[chatId].messages) {
      if (message.is_read === false) {
        message.is_view = false
      }
    }
    searchMessagesStore.addChat(chatId)
  }

  // Добавление только что созданного чата
  addNewChat(data) {
    const {chat_id: chatId, chat_name: chatName, creator} = data
    this.chats[chatId] = {
      "chat_name": chatName,
      messages: [],
      creator
    }

    this.initChat(chatId)
    console.log(`Добавлен новый чат: ${chatName}`)
  }

  // количество не просмотренных сообщений в чате, для отображения в Sidebar
  getChatNotViewedMessagesCount(chatId) {
    const chatNotViewedMessages = this.chats[chatId].messages.filter(message => message.is_view === false)
    return chatNotViewedMessages.length
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

  deleteChat(chatId) {
    console.log('Попытка удаления чата', chatId)
    if (this.selectedChatId === chatId) {
      this.setSelectedChatId(DEFAULT_CHAT_ID)
    }
    delete this.chats[chatId]
    searchMessagesStore.deleteChat(chatId)
    console.log('Удалён чат', chatId)
  }

  setSelectedChatId(chatId) {
    console.log('setSelectedChatId', chatId)
    this.selectedChatId = chatId
    this.selectedChatText = this.chats[chatId].text
    this.selectedChatTyping = false
    this.needScrollToNewMessage = false
  }

  // Метод для добавления чата, когда текущего пользователя добавляют в чат
  async addChat(chatId) {
    console.log('Попытка добавления чата', chatId)
    try{
      console.log(`Запрос данных чата`, chatId)
      const response = await MessageService.getChatMessages(chatId)
      console.log(response)

      this.chats[chatId] = response.data
      this.initChat(chatId)
    } catch (e) {
      console.log('Ошибка при загрузке данных чата', chatId)
      console.log(e.response)
    }
    console.log('Чат добавлен', chatId)
  }

  getMessageInCurrentChatById(messageId) {
    return this.getMessageInChat(messageId, this.selectedChatId)
  }

  getMessageInChat(messageId, chatId) {
    return this.chats[chatId].messages.find(message => message.message_id === messageId)
  }

  changeMessageText(data) {
    const {message_id: messageId, chat_id: chatId, text, change_time: changeTime} = data
    const message = this.getMessageInChat(messageId, chatId)
    message.text = text
    message.change_time = changeTime
    console.log(`Для сообщения ${messageId} из чата ${chatId} сменён текст на '${text}'`)
  }

  deleteMessage(data) {
    this.needScrollToNewMessage = false
    const {message_id: messageId, chat_id: chatId} = data
    this.chats[chatId].messages = this.chats[chatId].messages.filter(message => message.message_id !== messageId )
    console.log(`Из чата ${chatId} удалено сообщение ${messageId}`)
  }

  // is_read - пометка "прочитанности" для вычисления линии разделения новых и старых сообщений
  // is_view - были ли сообщение просмотрено для отображения количества новых сообщений в Sidebar
  addMessage(message, socketSendReadMessage) {
    if (!this.isLoadMessages) return

    const {chat_id: chatId, message_id: messageId} = message
    const notViewedMessagesCount = this.getChatNotViewedMessagesCount(chatId)

    this.needScrollToNewMessage = (
      notViewedMessagesCount === 0 && chatId === this.selectedChatId && this.isSelectedChatLastMessageInView()
      ||
      // Если пользоватль сам написал сообщений в чате, то надо показать сообщение даже если чат промотан
      message.login === authStore.user.login && chatId === this.selectedChatId
    )
    console.log('message store, addMessage, needScrollToNewMessage=', this.needScrollToNewMessage)

    if (message.type === 'TEXT') {
      if (message.login === authStore.user.login) {
        message.is_read = true
        message.is_view = true
      } else {
          if (this.needScrollToNewMessage) {
            message.is_read = true
            message.is_view = true
            socketSendReadMessage(messageId)
          } else {
            message.is_view = false
          }
      }
    }

    console.log(`MessagesStore add message to chatId "${chatId}":`, message)
    this.chats[chatId].messages.push(message)
  }

  getMessagesIdsWithTextInCurrentChat(text) {
    const ids = []
    for (let message of this.chats[this.selectedChatId].messages) {
      if (message.text.toLowerCase().includes(text.toLowerCase()) && message.type === 'TEXT') {
        ids.push(message.message_id)
      }
    }

    return ids
  }

  // waitReadList - сообщения которые уже просмотрены, но не помечены на фронте как прочитанные
  readAllMessagesInWaitList() {
    console.log("Помечаем прочитанными сообщения в waitReadList")
    for (let messageId of this.waitReadList) {
      this.markMessageAsRead(messageId)
    }
    this.waitReadList = []
  }

  markMessageAsRead(messageId) {
    this.setMessagePropertyValueInCurrentChat(messageId, "is_read", true)
    console.log(messageId, "помечено прочитанным")
  }

  // при просмотре сообщения оно сразу помечание как is_view=true, а так же отправляется пометка о прочтении в базу
  // на фронте оно пока добавляется в waitReadList, что бы в чате оставалась разделение новых и старых сообщений
  // сообщения waitReadList помечаются прочитанными в случае перехода в другой чат или отправки сообщения в текущем чате
  markMessageAsView(messageId, socketSendReadMessage) {
    this.addMessageToWaitReadList(messageId)
    this.setMessagePropertyValueInCurrentChat(messageId, "is_view", true)
    socketSendReadMessage(messageId)
    console.log('sendReadMessage for id:', messageId)
  }

  addMessageToInView(message) {
    const chatId = this.selectedChatId
    if (this.chats[chatId].messagesInView.indexOf(message) !== -1) return
    this.chats[chatId].messagesInView.push(message)

    const messages = this.chats[chatId].messagesInView.map(message => message.text)
    console.log(`addMessageToInView chatId=${this.getSelectedChatName()} message=${message.text}, messagesInView:`, messages)
    console.log('isLastMessageInView:', this.isSelectedChatLastMessageInView())
    console.log('selectedChatLastMessageInView:', this.getSelectedChatLastMessageInView()?.text)
  }

  deleteMessageFromInView(message) {
    const chatId = this.selectedChatId
    const {message_id: messageId} = message
    this.chats[chatId].messagesInView = this.chats[chatId].messagesInView.filter(message => message.message_id !== messageId)

    const messages = this.chats[chatId].messagesInView.map(message => message.text)
    console.log(`deleteMessageFromInView chatId=${this.getSelectedChatName()} message=${message.text}, messagesInView:`, messages)
    console.log('isLastMessageInView:', this.isSelectedChatLastMessageInView())
    console.log('selectedChatLastMessageInView:', this.getSelectedChatLastMessageInView()?.text)
  }

  getSelectedChatLastMessageId() {
    const selectedChatMessages = this.chats[this.selectedChatId].messages
    if (selectedChatMessages.length > 0) {
      const lastMessage = selectedChatMessages[selectedChatMessages.length - 1]
      return lastMessage.message_id
    }
    return undefined
  }

  isSelectedChatLastMessageInView() {
    const selectedChatMessagesInViewIds = this.chats[this.selectedChatId].messagesInView.map(message => message.message_id)
    const selectedChatLastMessageId = this.getSelectedChatLastMessageId()
    if (!selectedChatLastMessageId) return true
    return selectedChatMessagesInViewIds.includes(selectedChatLastMessageId)
  }

  getSelectedChatLastMessageInView() {
    const selectedChatMessagesInView = this.chats[this.selectedChatId].messagesInView
    const sortedMessagesInView = selectedChatMessagesInView.sort((a, b) => {
      const aMessageIndex = this.chats[this.selectedChatId].messages.indexOf(a)
      const bMessageIndex = this.chats[this.selectedChatId].messages.indexOf(b)
      if (aMessageIndex > bMessageIndex) return 1
      return -1
    })
    if (sortedMessagesInView.length > 0) return sortedMessagesInView[sortedMessagesInView.length - 1]
    return undefined
  }

  setMessagePropertyValueInCurrentChat(messageId, property, value) {
    for (let message of this.chats[this.selectedChatId].messages) {
      if (message.message_id === messageId) {
        message[property] = value
        return
      }
    }
  }

  addMessageToWaitReadList(messageId) {
    this.waitReadList.push(messageId)
    console.log('Добавлено к waitReadList', messageId)
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

  setIsLoadMessages(bool) {
    this.isLoadMessages = bool
  }

  setLoading(bool) {
    this.loading = bool
  }

  setLoadError(bool) {
    this.loadError = bool
  }

  setSelectedChatWasOpened() {
    this.chats[this.selectedChatId].wasOpened = true
  }

  isSelectedChatWasOpened() {
    return this.chats[this.selectedChatId].wasOpened
  }
}

export default new MessagesStore()
