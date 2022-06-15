import {makeAutoObservable} from "mobx"

import axiosInstance from '../axios/axios'
import authStore from './authStore'


//TODO ChatsStore
class MessagesStore {
  chats = {}
  selectedChatId = 'MAIN'
  isLoadMessages = false
  loading = false
  loadError = false
  selectedChatText = ''
  selectedChatTyping = false

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

  addMessage(message) {
    if (!this.isLoadMessages) return

    const {chat_id: chatId} = message
    console.log(`MessagesStore add message to chatId "${chatId}":`, message)
    this.chats[chatId].messages.push(message)
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
      this.chats[chatId].typingLogins = []
      this.chats[chatId].text = ''
    }
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
