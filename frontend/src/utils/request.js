import axios from 'axios'
import { ElMessage } from 'element-plus'

// 1. 创建 axios 实例
const service = axios.create({
  // 基础 URL，配合 vite.config.js 中的 proxy 代理
  // 发送请求时会自动带上 /api 前缀，例如 /api/login
  baseURL: '/api', 
  timeout: 5000 // 请求超时时间：5秒
})

// 2. 请求拦截器 (Request Interceptor)
// 在请求发送出去之前做一些事情，比如自动带上 Token
service.interceptors.request.use(
  (config) => {
    // 模拟：从 localStorage 获取 token (后续我们会用 Pinia 管理)
    const token = localStorage.getItem('token')
    if (token) {
      // Django JWT 标准通常是: "Bearer <token>"
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 3. 响应拦截器 (Response Interceptor)
// 在收到后端响应后做一些事情，比如统一处理报错
service.interceptors.response.use(
  (response) => {
    const res = response.data
    
    // 假设后端约定的成功状态码是 200
    // 如果不是 200，说明业务逻辑出错（如：密码错误、余额不足）
    // 注意：这里的 status 是 HTTP 状态码，res.code 是后端自定义的业务状态码
    // 我们这里简化处理，直接返回 data。实际项目中根据后端结构调整。
    return res
  },
  (error) => {
    console.error('API Error:', error)
    
    // 处理 HTTP 状态码错误
    let message = '系统未知错误'
    if (error.response) {
      switch (error.response.status) {
        case 400: message = '请求参数错误'; break;
        case 401: message = '未授权，请登录'; break;
        case 403: message = '拒绝访问'; break;
        case 404: message = '请求地址不存在'; break;
        case 500: message = '服务器内部错误'; break;
        default: message = `连接错误 ${error.response.status}`;
      }
    } else if (error.message.includes('timeout')) {
      message = '请求超时，请检查网络'
    }
    
    // 使用 Element Plus 弹出红色错误提示
    ElMessage({
      message: message,
      type: 'error',
      duration: 5 * 1000
    })
    
    return Promise.reject(error)
  }
)

export default service