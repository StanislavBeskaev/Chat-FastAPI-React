import axiosInstance from '../axios/axios'

export default class UserService {
  static async changeData(name, surname) {
    return axiosInstance.put('/user/change', {name, surname})
  }

  static async getUserInfo(login) {
    const response = await axiosInstance.get(`/user/info/${login}`)
    console.log('getUserInfo:', response)
    return response.data
  }

  static async changeAvatar(file) {
    const formData = new FormData()
    formData.append("file", file, file.name)
    return axiosInstance.post("/user/avatar", formData)
  }

  static async getAvatarFileName(login) {
    return axiosInstance.get(`user/avatar_file_name/${login}`)
  }
}
