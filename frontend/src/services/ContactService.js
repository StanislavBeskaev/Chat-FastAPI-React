import axiosInstance from '../axios/axios'

export default class ContactService {

  static async getContacts() {
    return axiosInstance.get('/contacts')
  }

  static async createContact(login) {
    return axiosInstance.post('/contacts', {login})
  }
}

