import axios from 'axios'
import {makeAutoObservable} from "mobx"

import {API_URL} from '../axios/axios'
import AuthService from '../services/AuthService'
import axiosInstance from '../axios/axios'
import UserService from '../services/UserService'
import messagesStore from './messagesStore'
import contactStore from './contactStore'


const LOCAL_STORAGE_ACCESS_TOKEN_KEY = 'token'

class AuthStore {
  user = null
  isAuth = false
  isLoading = false
  error = ''
  avatarFile = ''

  constructor() {
    makeAutoObservable(this)
    console.log("Создан authStore")
  }

  setAuth(bool) {
    this.isAuth = bool
  }

  setUser(user) {
    this.user = user
  }

  setLoading(bool) {
    this.isLoading = bool
  }

  setError(text) {
    this.error = text
  }

  setAvatarFile(file) {
    this.avatarFile = file
  }

  async saveAvatar(file) {
    const formData = new FormData()
    formData.append("file", file, file.name)
    const response = await axiosInstance.post("/user/avatar", formData)
    this.setAvatarFile(response.data.avatar_file)
  }

  //TODO вынести в userStore?
  async getAvatar() {
    const response = await axiosInstance.get("/user/avatar")
    this.setAvatarFile(response.data.avatar_file)
  }

  async registration(login, password, name, surname) {
    await this._auth(AuthService.registration, login, password, name, surname)
  }

  async login(login, password) {
    await this._auth(AuthService.login, login, password)
  }

  async _auth(service, ...args) {
    try {
      this.setError('')
      const response = await service(...args)
      console.log(response)
      localStorage.setItem(LOCAL_STORAGE_ACCESS_TOKEN_KEY, response.data['access_token'])
      this.setAuth(true)
      this.setUser(response.data.user)
      await this.getAvatar()
      //TODO подумать где инициализировать загрузку данных
      await messagesStore.loadMessages()
      await contactStore.loadContacts()
    } catch (e) {
      const errorText = JSON.stringify(e?.response?.data?.detail)
      console.log(errorText)
      this.setError(errorText)
      this.setAuth(false)
      this.setUser({})
    }
  }

  async checkAuth() {
    try {
      console.log("checkAuth")
      const response = await axios.get(`${API_URL}/auth/refresh`, {withCredentials: true})
      console.log('checkAuth response', response)
      localStorage.setItem(LOCAL_STORAGE_ACCESS_TOKEN_KEY, response.data['access_token'])
      this.setAuth(true)
      console.log("setAuth = true")
      this.setUser(response.data.user)
      await this.getAvatar()
      //TODO подумать где инициализировать загрузку данных
      await messagesStore.loadMessages()
      await contactStore.loadContacts()
    } catch (e) {
      console.log('checkAuth error', e?.response?.data?.detail)
    }
  }

  async logout() {
    this.setLoading(true)
    try {
      await AuthService.logout()
      this.setUser(null)
      this.setAuth(false)
      localStorage.removeItem(LOCAL_STORAGE_ACCESS_TOKEN_KEY);
    } catch (e) {
      const errorText = JSON.stringify(e?.response?.data?.detail)
      console.log(errorText)
      this.setError(errorText)
    } finally {
      this.setLoading(false)
    }
  }

  async changeUserData(name, surname) {
    this.setLoading(true)
    try {
      const response = UserService.changeData(name, surname)
      this.setUser((await response).data)
    } catch (e) {
      const errorText = JSON.stringify(e?.response?.data?.detail)
      console.log(errorText)
      this.setError(errorText)
    } finally {
      this.setLoading(false)
    }
  }
}

export default new AuthStore()
