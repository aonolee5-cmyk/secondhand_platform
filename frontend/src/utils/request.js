import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'


const service = axios.create({
  baseURL: '/api', 
  timeout: 60000 // 请求超时时间为60秒
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    // 成功响应直接返回数据
    return response.data
  },
  async (error) => {
    const originalRequest = error.config; // 获取原始请求配置

    // 处理401错误
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // 标记该请求已经重试过一次，防止死循环
      
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (refreshToken) {
        try {
          console.log('检测到 Access Token 过期，正在尝试刷新...');
          
          // 发送刷新令牌请求
          const res = await axios.post('http://127.0.0.1:8000/api/users/token/refresh/', {
            refresh: refreshToken
          });

          // 获取并存储新的token
          const newAccessToken = res.data.access;
          localStorage.setItem('token', newAccessToken);
          console.log('Token 刷新成功！');

          // 更新header并重新发送
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
          return service(originalRequest); 

        } catch (refreshError) {
          console.error('刷新令牌失效了，请重新登录');
          localStorage.clear();
          router.push('/login');
          ElMessage.error('登录状态已失效，请重新登录');
          return Promise.reject(refreshError);
        }
      }
    }

    // 处理其他错误
    console.error('API Error:', error)
    let message = '系统未知错误'
    
    if (error.response) {
      if (error.response.status === 401) {
        message = '身份验证已过期，请重新登录'
        localStorage.clear()
        router.push('/login')
      } else {
        switch (error.response.status) {
          case 400: message = '请求参数错误'; break;
          case 403: message = '权限不足，拒绝访问'; break;
          case 404: message = '请求资源不存在'; break;
          case 500: message = '服务器繁忙，请稍后再试'; break;
          default: message = `连接错误: ${error.response.status}`;
        }
      }
    } else if (error.message.includes('timeout')) {
      message = '网络请求超时，请检查您的网络'
    }

    // 显示错误信息
    if (!originalRequest._retry) {
      ElMessage({
        message: message,
        type: 'error',
        duration: 5 * 1000
      })
    }
    
    return Promise.reject(error)
  }
)

export default service