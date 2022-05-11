import axiosInstance from '../axios/axios'

export default class AuthService {
  static async login(login, password) {
    const formData = new FormData()
    formData.append('username', login)
    formData.append('password', password)
    return axiosInstance.post('/auth/login', formData)
  }

  static async registration(login, password) {
    return axiosInstance.post('/auth/registration', {login, password})
  }

  static async logout() {
    return axiosInstance.post('/auth/logout')
  }
}

