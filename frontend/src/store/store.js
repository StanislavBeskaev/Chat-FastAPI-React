import axios from 'axios'
import {makeAutoObservable} from "mobx"

import {API_URL} from '../axios/axios'
import AuthService from '../services/AuthService'


export default class Store {
  user = {}
  isAuth = false
  isLoading = false
  error = ''

  constructor() {
    makeAutoObservable(this)
  }

  setAuth(isAuth) {
    this.isAuth = isAuth
    this.setError('')
  }

  setUser(user) {
    this.user = user
  }

  setLoading(isLoading) {
    this.isLoading = isLoading
  }

  setError(text) {
    this.error = text
  }

  async registration(login, password) {
    try {
      const response = await AuthService.registration(login, password)
      console.log(response)
      localStorage.setItem('token', response.data['access_token'])
      this.setAuth(true)
      this.setUser(response.data.user)
    } catch (e) {
      const errorText = e.response?.data?.detail
      console.log(errorText)
      this.setError(errorText)
    }
  }

  async login(login, password) {
    try {
      const response = await AuthService.login(login, password)
      console.log(response)
      localStorage.setItem('token', response.data['access_token'])
      this.setAuth(true)
      this.setUser(response.data.user)
    } catch (e) {
      const errorText = e.response?.data?.detail
      console.log(errorText)
      this.setError(errorText)
    }
  }

  async checkAuth() {
    this.setLoading(true)
    try {
      const response = await axios.get(`${API_URL}/auth/refresh`, {withCredentials: true})
      console.log('checkAuth response', response)
      localStorage.setItem('token', response.data['access_token'])
      this.setAuth(true)
      this.setUser(response.data.user)
    } catch (e) {
      console.log('checkAuth error', e.response?.data?.detail)
    } finally {
      this.setLoading(false)
    }
  }
}