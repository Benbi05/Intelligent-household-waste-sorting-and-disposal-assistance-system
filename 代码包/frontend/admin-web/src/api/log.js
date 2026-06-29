import request from './request'

/** 获取操作日志列表 */
export function getLogList(params = {}) {
  return request.get('/admin/logs', { params })
}
