import axiosInstance from '../axios/axios'

export default class ChatService {

  static async createNewChat(name, members) {
    return axiosInstance.post("/chats/", {"chat_name": name, members})
  }

  static async changeChatName(chatId, newName) {
    return axiosInstance.put(`/chats/${chatId}`, {"chat_name": newName})
  }

  static async tryLeaveChat(chatId) {
    return axiosInstance.get(`/chats/try_leave/${chatId}`)
  }

  static leaveChat(chatId) {
    return axiosInstance.post(`/chats/leave/${chatId}`)
  }
}
