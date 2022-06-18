import axiosInstance from '../axios/axios'

export default class MessageService {
  static async getMessages() {
    return axiosInstance.get("/messages/")
  }

  static async createNewChat(name, members) {
    return axiosInstance.post("/messages/chats/", {"chat_name": name, members})
  }
}
