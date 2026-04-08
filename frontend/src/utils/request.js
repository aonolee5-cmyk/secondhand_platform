import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const service = axios.create({
  baseURL: '/api',
  timeout: 60000
})

// --- 请求拦截器 (你代码里好像没发这部分，补上) ---
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
    const originalRequest = error.config
    
    // 1. 处理 401 身份过期 (自动无感刷新 Token)
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      // 如果是登录接口报 401，说明密码错或账号封禁，直接跳过刷新逻辑
      if (originalRequest.url.includes('/users/login/')) {
        return handleGeneralError(error)
      }

      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      
      if (refreshToken) {
        try {
          // 使用相对路径，走 Vite 代理
          const res = await axios.post('/api/users/token/refresh/', { refresh: refreshToken })
          const newAccessToken = res.data.access
          localStorage.setItem('token', newAccessToken)
          
          // 重试原始请求
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`
          return service(originalRequest)
        } catch (refreshError) {
          // 刷新令牌也失效了，强制登出
          localStorage.clear()
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      }
    }

    // 2. 处理常规错误 (包含账号封禁 400)
    return handleGeneralError(error)
  }
)

/**
 * 核心：企业级通用错误处理函数
 */
function handleGeneralError(error) {
  let message = '系统未知错误'
  
  if (error.response) {
    const data = error.response.data
    // 优先级 1：后端定义的 detail (如：账号已被封禁)
    // 优先级 2：后端定义的 message
    // 优先级 3：表单验证错误 (提取第一个错误)
    if (data.detail) {
      message = data.detail
    } else if (data.message) {
      message = data.message
    } else if (typeof data === 'object') {
      // 这里的逻辑能把 {"username": ["太长了"]} 这种错误转成文字
      const firstKey = Object.keys(data)[0]
      if (Array.isArray(data[firstKey])) {
        message = `${firstKey}: ${data[firstKey][0]}`
      }
    }

    // 403 权限不足处理
    if (error.response.status === 403) {
      message = '权限不足，拒绝访问'
    }
  } else if (error.message.includes('timeout')) {
    message = '网络请求超时，请检查您的网络'
  }

  // 弹出错误提示
  ElMessage({
    message: message,
    type: 'error',
    duration: 5000
  })

  // 返回 rejected 状态，让 login.vue 进 catch
  return Promise.reject(error)
}

export default service