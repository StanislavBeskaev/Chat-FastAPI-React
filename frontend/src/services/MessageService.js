import axiosInstance from '../axios/axios'

export default class MessageService {
  static async getMessages() {
    return axiosInstance.get("/messages/")
  }

  static async getChatMessages(chatId) {
    return axiosInstance.get(`/messages/${chatId}`)
  }
}
