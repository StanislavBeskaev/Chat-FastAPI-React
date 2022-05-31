import {makeAutoObservable} from "mobx"

import axiosInstance from '../axios/axios'


//TODO ChatsStore
class MessagesStore {
  messages = {}
  chats = []
  selectedChatId = 'MAIN'
  isLoadMessages = false
  loading = false
  loadError = false

  constructor() {
    makeAutoObservable(this)
    console.log("Создан MessagesStore")
  }

  async loadMessages() {
    console.log("load messages")
    this.setLoading(true)
    try{
      const response = await axiosInstance.get("/messages/")
      console.log("success load, response:", response)
      this.setMessages(response.data)
      this.setChats(Object.keys(response.data))
      this.setLoadError(false)
      this.setIsLoadMessages(true)
    } catch (e) {
      console.log("Ошибка при зарузке сообщений:", e)
      this.setLoadError(true)
    } finally {
      this.setLoading(false)
    }
  }

  addMessage(message) {
    if (!this.isLoadMessages) return

    const {chat_id: chatId} = message
    console.log(`MessagesStore add message to chatId "${chatId}":`, message)
    this.messages[chatId].push(message)
  }

  setMessages(data) {
    this.messages = data
  }

  setChats(chats) {
    this.chats = chats
  }

  setSelectedChatId(chatId) {
    this.selectedChatId = chatId
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
