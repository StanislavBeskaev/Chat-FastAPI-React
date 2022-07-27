import axiosInstance from '../axios/axios'

export default class MessageService {
  static async getMessages() {
    return axiosInstance.get("/messages/")
  }

  static async getChatMessages(chatId) {
    return axiosInstance.get(`/messages/${chatId}`)
  }

  static async changeMessageText(messageId, text) {
    return axiosInstance.put(`/messages/${messageId}`, {text})
  }

  static async deleteMessage(messageId) {
    return axiosInstance.delete(`/messages/${messageId}`)
  }
}
