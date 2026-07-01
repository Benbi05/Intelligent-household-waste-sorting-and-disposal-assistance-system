import request from './request'

/** 获取商家列表 */
export function getMerchantList(params = {}) {
  return request.get('/admin/merchants', { params })
}

/** 审核商家 */
export function auditMerchant(merchantId, data) {
  return request.put(`/admin/merchants/${merchantId}/audit`, data)
}

/** 获取商家统计概览 */
export function getMerchantStats(params = {}) {
  return request.get('/admin/merchants/stats', { params })
}
