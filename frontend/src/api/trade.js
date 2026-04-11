import request from '@/utils/request'

export function createOrder(data) {
  return request({ 
    url: '/trade/orders/', 
    method: 'post', 
    data 
  })
}

// 获取订单列表
export function getOrderList(params) {
  return request({ 
    url: '/trade/orders/', 
    method: 'get', 
    params 
  })
}

// 支付订单
export function payOrder(id) {
  return request({ 
    url: `/trade/orders/${id}/pay/`, 
    method: 'post' 
  })
}

// 确认收货
export function receiveOrder(id) {
    return request({
        url: `/trade/orders/${id}/receive/`, 
        method: 'post'
    })
}

// 申请退款
export function applyRefund(id,data) {
  return request({
    url:`/trade/orders/${id}/apply_refund/`,
    method: 'post',
    data
  })
}

// 处理退款
export function handleRefund(id,data) {
  return request({
    url:`/trade/orders/${id}/handle_refund/`,
    method: 'post',
    data
  })
}

// 查询收藏状态
export function checkFavoriteStatus(productId) {
  return request({ 
    url: '/trade/favorites/check_status/', 
    method: 'get', 
    params: { product_id: productId } 
  })
}

// 切换收藏状态
export function toggleFavorite(productId) {
  return request({ 
    url: '/trade/favorites/toggle/', 
    method: 'post', 
    data: { product_id: productId } 
  })
}

// 添加购物车
export function addToCart(data) {
  return request({ 
    url: '/trade/cart/', 
    method: 'post', 
    data 
  })
}