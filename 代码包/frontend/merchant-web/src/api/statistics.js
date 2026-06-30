import request from './request'

/** 获取商家仪表盘统计 */
export function getMerchantStats() {
  return request.get('/merchant/statistics')
}

/** 获取经营报表 */
export function getReports() {
  return request.get('/merchant/reports')
}
