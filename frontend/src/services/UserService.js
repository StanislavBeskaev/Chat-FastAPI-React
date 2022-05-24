import axiosInstance from '../axios/axios'

export default class UserService {
  static async changeData(name, surname) {
    return axiosInstance.put('/user/change', {name, surname})
  }

  static async getLoginAvatarFile(login) {
    const response = await axiosInstance.get(`/user/avatar/${login}`)
    console.log(response)
    return response.data.avatar_file
  }
}
