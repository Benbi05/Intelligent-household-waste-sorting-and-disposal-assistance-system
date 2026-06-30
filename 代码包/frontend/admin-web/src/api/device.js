import request from './request'

/** 获取设备列表 */
export function getDeviceList(params = {}) {
  return request.get('/admin/devices', { params })
}

/** 获取设备详情 */
export function getDeviceDetail(deviceId) {
  return request.get(`/admin/devices/${deviceId}`)
}

/** 新增设备 */
export function createDevice(data) {
  return request.post('/admin/devices', data)
}

/** 更新设备状态（启用/禁用） */
export function updateDeviceStatus(deviceId, status) {
  return request.put(`/admin/devices/${deviceId}/status`, { status })
}

/** 删除设备 */
export function deleteDevice(deviceId) {
  return request.delete(`/admin/devices/${deviceId}`)
}

/** 更新设备配置 */
export function updateDeviceConfig(deviceId, data) {
  return request.put(`/admin/devices/${deviceId}/config`, data)
}

/** 固件升级 */
export function firmwareUpgrade(deviceIds, firmwareVersion) {
  return request.post('/admin/devices/firmware-upgrade', { deviceIds, firmwareVersion })
}

/** 获取设备统计概览 */
export function getDeviceStats() {
  return request.get('/admin/devices/stats')
}
