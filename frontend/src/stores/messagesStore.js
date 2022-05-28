import {makeAutoObservable} from "mobx"

import axiosInstance from '../axios/axios'


//TODO сделать разделение сообщений по чатам
class MessagesStore {
  messages = []

  constructor() {
    makeAutoObservable(this)
    console.log("Создан MessagesStore")
  }

  async loadMessages() {
    console.log("load messages")
    const response = await axiosInstance.get("/messages/")
    console.log("response:", response)
    this.setMessages(response.data)
  }

  setMessages(data) {
    this.messages = data
  }

  addMessage(message) {
    console.log("MessagesStore add message:", message)
    this.messages.push(message)
  }
}

export default new MessagesStore()
