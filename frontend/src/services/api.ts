import axios from 'axios'
import { useInterviewStore } from '../stores/interview'
import { useAuthStore } from '../stores/auth'
import { getRuntimeApiBaseUrl } from './runtimeConfig'

const api = axios.create({
  timeout: 120000
})

api.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  const interviewStore = useInterviewStore()
  const url = config.url || ''
  if (!/^https?:\/\//i.test(url)) {
    config.baseURL = getRuntimeApiBaseUrl()
  }
  // 仅 @require_session 端点使用面试 session token，其余一律用用户 JWT
  const needsSessionToken =
    url.startsWith('/api/chat') ||
    url.startsWith('/api/end') ||
    url.startsWith('/api/speech/') ||
    url.startsWith('/api/resume/export')
  if (needsSessionToken) {
    if (interviewStore.token) {
      config.headers.Authorization = `Bearer ${interviewStore.token}`
    } else if (config.headers && 'Authorization' in config.headers) {
      delete config.headers.Authorization
    }
  } else if (authStore.jwt) {
    config.headers.Authorization = `Bearer ${authStore.jwt}`
  }
  return config
})

export default api
