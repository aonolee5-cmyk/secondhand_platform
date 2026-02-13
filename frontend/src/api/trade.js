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