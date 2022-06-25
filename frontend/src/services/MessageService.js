import axiosInstance from '../axios/axios'

export default class MessageService {
  static async getMessages() {
    return axiosInstance.get("/messages/")
  }

  static async createNewChat(name, members) {
    return axiosInstance.post("/messages/chats/", {"chat_name": name, members})
  }

  static async changeChatName(chatId, newName) {
    return axiosInstance.put(`/messages/chats/${chatId}`, {"chat_name": newName})
  }

  static async getChatMembers(chatId) {
    return axiosInstance.get(`/messages/chat_members/${chatId}`)
  }

  static async addChatMember(chatId, login) {
    return axiosInstance.post(`/messages/chat_members/${chatId}`, {login})
  }

  static async deleteChatMember(chatId, login) {
    return axiosInstance.delete(`/messages/chat_members/${chatId}`, {data: {login}})
  }
}
