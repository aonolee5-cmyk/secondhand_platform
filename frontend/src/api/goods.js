import request from '@/utils/request'

export function getCategories() {
  return request({ url: '/goods/categories/', method: 'get' })
}

export function uploadImage(data) {
  return request({ 
    url: '/goods/products/upload_image/', 
    method: 'post',
    headers: { 'Content-Type': 'multipart/form-data' },
    data 
  })
}

export function postProduct(data) {
  return request({ url: '/goods/products/', 
    method: 'post', 
    data })
}