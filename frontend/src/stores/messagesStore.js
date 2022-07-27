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

  // количество не просмотренных сообщений в чате, для отображения в Sidebar
  getChatNotViewedMessagesCount(chatId) {
    const ChatNotViewedMessages = this.chats[chatId].messages.filter(message => message.is_view === false)
    return ChatNotViewedMessages.length
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

  getMessageInCurrentChatById(messageId) {
    return this.getMessageInChat(messageId, this.selectedChatId)
  }

  getMessageInChat(messageId, chatId) {
    return this.chats[chatId].messages.find(message => message.message_id === messageId)
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

  deleteChat(chatId) {
    console.log('Попытка удаления чата', chatId)
    if (this.selectedChatId === chatId) {
      this.setSelectedChatId(DEFAULT_CHAT_ID)
    }
    delete this.chats[chatId]
    searchMessagesStore.deleteChat(chatId)
    console.log('Удалён чат', chatId)
  }

  async addChat(chatId) {
    console.log('Попытка добавления чата', chatId)
    try{
      console.log(`Запрос данных чата`, chatId)
      const response = await MessageService.getChatMessages(chatId)
      console.log(response)

      this.chats[chatId] = response.data
      this.initChat(chatId)
      searchMessagesStore.addChat(chatId)
    } catch (e) {
      console.log('Ошибка при загрузке данных чата', chatId)
      console.log(e.response)
    }
    console.log('Чат добавлен', chatId)
  }

  // is_read - пометка "прочитанности" для вычисления линии разделения новых и старых сообщений
  // is_view - были ли сообщение просмотрено
  addMessage(message, socketSendReadMessage) {
    if (!this.isLoadMessages) return

    const {chat_id: chatId, message_id: messageId} = message
    const notViewedMessagesCount = this.getChatNotViewedMessagesCount(chatId)
    // TODO придумать механизм для понимания, что чат прокручен не до конца, а где-то в середине
    //  и по этому определять, нужно ли докрутить чат до нового сообщения
    //  так же это применить в компоненте Messages для определения needScrollToLastMessage
    this.needScrollToNewMessage = notViewedMessagesCount === 0 && chatId === this.selectedChatId

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
    for (let message of this.chats[chatId].messages) {
      if (message.is_read === false) {
        message.is_view = false
      }
    }
  }

  setSelectedChatId(chatId) {
    this.selectedChatId = chatId
    this.selectedChatText = this.chats[chatId].text
    this.selectedChatTyping = false
    this.needScrollToNewMessage = false
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
