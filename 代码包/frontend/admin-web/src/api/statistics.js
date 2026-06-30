import request from './request'

/** 获取统计概览 */
export function getOverview(params = {}) {
  return request.get('/admin/statistics/overview', { params })
}

/** 获取投放统计 */
export function getDeliveryStats(params = {}) {
  return request.get('/admin/statistics/delivery', { params })
}

/** 导出数据 */
export function exportData() {
  return request.get('/admin/statistics/export')
}
