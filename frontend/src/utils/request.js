import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const service = axios.create({
  baseURL: '/api',
  timeout: 60000
})

let isRefreshing = false
let requestsQueue = []

// --- 请求拦截器 ---
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// --- 响应拦截器 ---
service.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const { config, response } = error
    
    // 🚀 处理 401 身份过期
    if (response && response.status === 401) {
      // 如果是登录接口报 401，说明密码错或账号封禁，直接报错
      if (config.url.includes('/users/login/')) {
        return handleGeneralError(error)
      }

      // 如果正在刷新中，将当前请求存入队列，等待刷新完成后重发
      if (isRefreshing) {
        return new Promise((resolve) => {
          requestsQueue.push((newToken) => {
            config.headers['Authorization'] = `Bearer ${newToken}`
            resolve(service(config))
          })
        })
      }

      // 开始刷新逻辑
      isRefreshing = true
      const refreshToken = localStorage.getItem('refresh_token')
      
      if (refreshToken) {
        try {
          // 注意：这里使用原生 axios 避免进入 service 的拦截器死循环
          const res = await axios.post('/api/users/token/refresh/', { refresh: refreshToken })
          const newToken = res.data.access
          
          localStorage.setItem('token', newToken)
          
          // 🚀 核心：执行队列中所有的请求
          requestsQueue.forEach((callback) => callback(newToken))
          requestsQueue = [] // 清空队列
          
          // 执行当前请求
          config.headers['Authorization'] = `Bearer ${newToken}`
          return service(config)
        } catch (refreshError) {
          // 刷新失败（Refresh Token 也过期了），彻底清除状态并跳回登录
          requestsQueue = []
          localStorage.clear()
          // 加上标记防止循环跳转
          if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login'
          }
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      } else {
        // 没有 refresh_token，直接去登录
        localStorage.clear()
        // window.location.href = '/login'
      }
    }

    // 2. 处理常规错误 (400 封禁, 403 权限不足, 500 服务器错误)
    return handleGeneralError(error)
  }
)

/**
 * 核心：通用错误提示处理
 */
function handleGeneralError(error) {
  // 🚀 防抖处理：如果已经在刷新或跳转中，不弹出多余的错误提示
  if (isRefreshing) return Promise.reject(error)

  let message = '系统未知错误'
  if (error.response) {
    const data = error.response.data
    message = data.detail || data.message || message
    
    // 处理 Django 的校验错误 {"username": ["该字段必填"]}
    if (typeof data === 'object' && !data.detail && !data.message) {
      const firstKey = Object.keys(data)[0]
      if (Array.isArray(data[firstKey])) {
        message = `${data[firstKey][0]}`
      }
    }
  }

  // 避免登录页重复弹出消息
  if (!window.isMessageShowing) {
    window.isMessageShowing = true
    ElMessage({
      message: message,
      type: 'error',
      duration: 3000,
      onClose: () => { window.isMessageShowing = false }
    })
  }

  return Promise.reject(error)
}

export default service