import axiosInstance from '../axios/axios'

export default class ChatMembersService {
  static async getChatMembers(chatId) {
    return axiosInstance.get(`/chat_members/${chatId}`)
  }

  static async addChatMember(chatId, login) {
    return axiosInstance.post(`/chat_members/${chatId}`, {login})
  }

  static async deleteChatMember(chatId, login) {
    return axiosInstance.delete(`/chat_members/${chatId}`, {data: {login}})
  }
}
