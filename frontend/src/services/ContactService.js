import axiosInstance from '../axios/axios'

export default class ContactService {

  static async getContacts() {
    return axiosInstance.get('/contacts/')
  }

  static async createContact(login) {
    return axiosInstance.post('/contacts/', {login})
  }

  static async deleteContact(login) {
    return axiosInstance.delete('/contacts/', {data: {login}})
  }

  static async getOne(login) {
    return axiosInstance.get(`/contacts/${login}`)
  }

  static async changeContact(login, name, surname) {
    return axiosInstance.put('/contacts/', {login, name, surname})
  }
}
