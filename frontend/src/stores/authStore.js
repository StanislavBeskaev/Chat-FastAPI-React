import axios from 'axios'
import {makeAutoObservable} from "mobx"

import {API_URL} from '../axios/axios'
import AuthService from '../services/AuthService'
import UserService from '../services/UserService'
import messagesStore from './messagesStore'
import contactStore from './contactStore'


const LOCAL_STORAGE_ACCESS_TOKEN_KEY = 'token'

class AuthStore {
  user = null
  isAuth = false
  isLoading = false
  error = ''
  avatarFile = null

  constructor() {
    makeAutoObservable(this)
    console.log("Создан authStore")
  }

  async changeAvatar(file) {
    console.log("Попытка изменения аватара")
    const response = await UserService.changeAvatar(file)
    console.log(response)
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
      await this.handleSuccessAuth(response)
    } catch (e) {
      const errorText = e?.response?.data?.detail
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
      await this.handleSuccessAuth(response)
    } catch (e) {
      console.log('checkAuth error', e?.response?.data?.detail)
    }
  }

  async handleSuccessAuth(response) {
    localStorage.setItem(LOCAL_STORAGE_ACCESS_TOKEN_KEY, response.data['access_token'])
    this.setAuth(true)
    console.log("setAuth = true")
    this.setUser(response.data.user)
    await this.loadInitialData()
  }

  async loadInitialData() {
    await this.loadAvatarFileName()
    await messagesStore.loadMessages()
    await contactStore.loadContacts()
  }

  async loadAvatarFileName() {
    try {
      console.log("Грузим название файла своего аватара")
      const response = await UserService.getAvatarFileName(this.user.login)
      console.log("Свой аватар:", response)
      this.setAvatarFile(response.data.avatar_file)
    } catch (e) {
      console.log("Ошибка при зарузке имени файла своего аватара", e.res)
    }
  }

  async logout() {
    this.setLoading(true)
    try {
      messagesStore.setDefaultState()
      await AuthService.logout()
      this.setUser(null)
      this.setAuth(false)
      localStorage.removeItem(LOCAL_STORAGE_ACCESS_TOKEN_KEY);
    } catch (e) {
      const errorText = e?.response?.data?.detail
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
      const errorText = e?.response?.data?.detail
      console.log(errorText)
      this.setError(errorText)
    } finally {
      this.setLoading(false)
    }
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

  setAvatarFile(avatarFile) {
    console.log("setAvatarFile", avatarFile)
    this.avatarFile = avatarFile
  }
}

export default new AuthStore()
