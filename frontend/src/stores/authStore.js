import axios from 'axios'
import {makeAutoObservable} from "mobx"

import {API_URL} from '../axios/axios'
import AuthService from '../services/AuthService'
import UserService from '../services/UserService'
import messagesStore from './messagesStore'
import contactStore from './contactStore'
import socketStore from './socketStore'
import logMessages from '../log'


const LOCAL_STORAGE_ACCESS_TOKEN_KEY = 'token'

class AuthStore {
  user = null
  isAuth = false
  isLoading = false
  error = ''
  avatarFile = null

  constructor() {
    makeAutoObservable(this)
    logMessages("Создан authStore")
  }

  async changeAvatar(file) {
    logMessages("Попытка изменения аватара")
    const response = await UserService.changeAvatar(file)
    logMessages(response)
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
      logMessages(response)
      await this.handleSuccessAuth(response)
    } catch (e) {
      const errorText = e?.response?.data?.detail
      logMessages(errorText)
      this.setError(errorText)
      this.setAuth(false)
      this.setUser({})
    }
  }

  async checkAuth() {
    try {
      logMessages("checkAuth")
      const response = await axios.get(`${API_URL}/auth/refresh`, {withCredentials: true})
      logMessages('checkAuth response', response)
      await this.handleSuccessAuth(response)
    } catch (e) {
      logMessages('checkAuth error', e?.response?.data?.detail)
    }
  }

  async handleSuccessAuth(response) {
    localStorage.setItem(LOCAL_STORAGE_ACCESS_TOKEN_KEY, response.data['access_token'])
    this.setAuth(true)
    logMessages("setAuth = true")
    this.setUser(response.data.user)
    await this.loadInitialData()
    await socketStore.connect(response.data.user.login)
  }

  async loadInitialData() {
    await this.loadAvatarFileName()
    await messagesStore.loadMessages()
    await contactStore.loadContacts()
  }

  async loadAvatarFileName() {
    try {
      logMessages("Грузим название файла своего аватара")
      const response = await UserService.getAvatarFileName(this.user.login)
      logMessages("Свой аватар:", response)
      this.setAvatarFile(response.data.avatar_file)
    } catch (e) {
      logMessages("Ошибка при зарузке имени файла своего аватара", e.res)
    }
  }

  async logout() {
    this.setLoading(true)
    try {
      messagesStore.setDefaultState()
      await AuthService.logout()
      this.setUser(null)
      this.setAuth(false)
      localStorage.removeItem(LOCAL_STORAGE_ACCESS_TOKEN_KEY)
      // disconnect в конце, потому что на авторизации завязана логика reconnect к сокету
      socketStore.disconnect()
    } catch (e) {
      const errorText = e?.response?.data?.detail
      logMessages(errorText)
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
      logMessages(errorText)
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
    logMessages("setAvatarFile", avatarFile)
    this.avatarFile = avatarFile
  }
}

export default new AuthStore()
