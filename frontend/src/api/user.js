import request from '@/utils/request'

// 获取用户个人信息
export function getProfile() {
  return request({ url: '/users/profile/', 
    method: 'get' })
}

// 修改用户个人信息
export function updateProfile(data) {
  return request({ url: '/users/profile/', 
    method: 'put', 
    data })
}

// 修改用户头像
export function updateAvatar(formData) {
  return request({
    url: '/users/profile/',
    method: 'patch',
    headers: { 'Content-Type': 'multipart/form-data' },
    data: formData
  })
}

// 获取用户收货地址列表
export function getAddresses() {
  return request({ url: '/users/addresses/', 
    method: 'get' 
  })
}

// 添加用户收货地址
export function addAddress(data){
  return request({url: '/users/addresses/',
    method: 'post',
    data
  })
}

// 删除用户收货地址
export function deleteAddress(id){
  return request({url: `/users/addresses/${id}/`,
    method: 'delete'
  })
}

// 设置默认地址
export function setDefaultAddress(id){
  return request({url: `/users/addresses/${id}/set_default/`,
    method: 'post'
  })
}

// 用户实名验证提交
export function submitVerify(data) {
  return request({
    url: '/users/verify/',
    method: 'post',
    data
  })
}

// 用户举报提交
export function submitReport(data){
  return request({
    url: '/users/reports/',
    method: 'post',
    data
  })
}