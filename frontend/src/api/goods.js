import request from '@/utils/request'

// 商品分类列表
export function getCategories() {
  return request({ url: '/goods/categories/', 
    method: 'get' 
  })
}

// 发布商品 - 上传图片
export function uploadImage(data) {
  return request({ 
    url: '/goods/products/upload_image/', 
    method: 'post',
    headers: { 'Content-Type': 'multipart/form-data' },
    data 
  })
}

// 发布商品
export function postProduct(data) {
  return request({ url: '/goods/products/', 
    method: 'post', 
    data 
  })
}

// 搜索/获取商品列表
export function searchProducts(params) {
  return request({
    url: '/goods/list/',
    method: 'get',
    params 
  })
}


// 获取我发布的商品列表
export function getMyProducts() {
  return request({ url: '/goods/list/?mine=1', 
    method: 'get' 
  })
}

// 修改商品状态
export function updateProductStatus(id, status) {
  return request({ 
    url: `/goods/list/${id}/change_status/`, 
    method: 'post', 
    data: { status } 
  })
}

// 获取商品详情
export function getProductDetail(id){
  return request({ url: `/goods/products/${id}/`, 
    method: 'get' 
  })
}

//修改商品信息
export function updateProduct(id, data){
  return request({ url: `/goods/products/${id}/`, 
    method: 'patch', 
    data
  })
}