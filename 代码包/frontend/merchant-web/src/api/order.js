import request from './request'

/** 获取订单列表 */
export function getOrders(params = {}) {
  return request.get('/merchant/orders', { params })
}

/** 核销订单 */
export function verifyOrder(verifyCode) {
  return request.post('/merchant/orders/verify', { verifyCode })
}
