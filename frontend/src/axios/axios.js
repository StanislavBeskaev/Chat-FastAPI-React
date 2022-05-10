import axios from 'axios'

export const API_URL = `http://localhost:8000/api`

const axiosInstance = axios.create({
  withCredentials: true,
  baseURL: API_URL
})

axiosInstance.interceptors.request.use((config) => {
  config.headers.Authorization = `Bearer ${localStorage.getItem('token')}`
  return config
})

axiosInstance.interceptors.response.use((config) => {
  return config;
},async (error) => {
  const originalRequest = error.config
  if (error.response.status === 401 && error.config && !error.config._isRetry) {
    originalRequest._isRetry = true;
    try {
      const response = await axios.get(`${API_URL}/auth/refresh`, {withCredentials: true})
      localStorage.setItem('token', response.data['access_token'])
      return axiosInstance.request(originalRequest);
    } catch (e) {
      console.log('НЕ АВТОРИЗОВАН')
    }
  }
  throw error
})

export default axiosInstance
