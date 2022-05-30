import {makeAutoObservable} from "mobx"

import axiosInstance from '../axios/axios'


//TODO ChatsStore
class MessagesStore {
  messages = {}
  chats = []
  selectedChatId = 'MAIN'
  isLoadData = false

  constructor() {
    makeAutoObservable(this)
    console.log("Создан MessagesStore")
  }

  async loadMessages() {
    console.log("load messages")
    const response = await axiosInstance.get("/messages/")
    console.log("response:", response)
    this.setMessages(response.data)
    this.setChats(Object.keys(response.data))
    this.setIsLoadData(true)
  }

  setIsLoadData(bool) {
    this.isLoadData = bool
  }

  setChats(chats) {
    this.chats = chats
  }

  setSelectedChatId(chatId) {
    this.selectedChatId = chatId
  }

  setMessages(data) {
    this.messages = data
  }

  addMessage(message) {
    if (!this.isLoadData) return

    const {chat_id: chatId} = message
    console.log(`MessagesStore add message to chatId "${chatId}":`, message)
    this.messages[chatId].push(message)
  }
}

export default new MessagesStore()
