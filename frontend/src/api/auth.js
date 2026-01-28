import request from '@/utils/request'

// 用户登录
export function login(data) {
  return request({
    url: '/users/login/', // 对应 Django 后端的路由
    method: 'post',
    data // 包含 username, password
  })
}

// 用户注册
export function register(data) {
  return request({
    url: '/users/register/',
    method: 'post',
    data
  })
}

//以此类推，以后所有的用户相关接口都写在这里