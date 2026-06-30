import request from './request'

/** 获取商品列表 */
export function getCommodities(params = {}) {
  return request.get('/merchant/commodities', { params })
}

/** 新增商品 */
export function createCommodity(data) {
  return request.post('/merchant/commodities', data)
}

/** 更新商品 */
export function updateCommodity(id, data) {
  return request.put(`/merchant/commodities/${id}`, data)
}
