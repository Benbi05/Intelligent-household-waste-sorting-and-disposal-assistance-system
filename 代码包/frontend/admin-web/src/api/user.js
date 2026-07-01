import request from './request'

/** 获取居民用户列表 */
export function getUserList(params = {}) {
  return request.get('/admin/users', { params })
}

/** 获取用户详情 */
export function getUserDetail(userId) {
  return request.get(`/admin/users/${userId}`)
}

/** 更新用户状态（启用/禁用） */
export function updateUserStatus(userId, status) {
  return request.put(`/admin/users/${userId}/status`, { status })
}

/** 获取用户统计概览 */
export function getUserStats(params = {}) {
  return request.get('/admin/users/stats', { params })
}
