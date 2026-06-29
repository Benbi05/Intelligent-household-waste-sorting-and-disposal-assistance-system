import request from './request'

/** 获取区域列表 */
export function getAreaList() {
  return request.get('/admin/areas')
}

/** 创建区域 */
export function createArea(data) {
  return request.post('/admin/areas', data)
}

/** 更新区域 */
export function updateArea(areaId, data) {
  return request.put(`/admin/areas/${areaId}`, data)
}

/** 删除区域 */
export function deleteArea(areaId) {
  return request.delete(`/admin/areas/${areaId}`)
}
