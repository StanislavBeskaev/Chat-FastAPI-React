import axiosInstance from '../axios/axios'

export default class UserService {
  static async changeData(name, surname) {
    return axiosInstance.put('/user/change', {name, surname})
  }
}
