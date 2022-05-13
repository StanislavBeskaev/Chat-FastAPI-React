import axios from 'axios'
import {makeAutoObservable} from "mobx"

import {API_URL} from '../axios/axios'
import AuthService from '../services/AuthService'
import axiosInstance from '../axios/axios'


const LOCAL_STORAGE_ACCESS_TOKEN_KEY = 'token'

export default class Store {
  user = null
  isAuth = false
  isLoading = false
  error = ''

  constructor() {
    makeAutoObservable(this)
    console.log("Создан store")
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

  async registration(login, password) {
    try {
      const response = await AuthService.registration(login, password)
      console.log(response)
      localStorage.setItem(LOCAL_STORAGE_ACCESS_TOKEN_KEY, response.data['access_token'])
      this.setAuth(true)
      this.setUser(response.data.user)
      this.setError('')
    } catch (e) {
      const errorText = JSON.stringify(e?.response?.data?.detail)
      console.log(errorText)
      this.setError(errorText)
      this.setAuth(false)
      this.setUser({})
    }
  }

  async login(login, password) {
    try {
      const response = await AuthService.login(login, password)
      console.log(response)
      localStorage.setItem(LOCAL_STORAGE_ACCESS_TOKEN_KEY, response.data['access_token'])
      this.setAuth(true)
      this.setUser(response.data.user)
      this.setError('')
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

  //TODO убрать после тестов
  async callTest() {
    try {
      const response = await axiosInstance.get("/test")
      alert(response.data.message)
    } catch (e) {
      alert(e.response?.data?.detail)
    }

  }
}