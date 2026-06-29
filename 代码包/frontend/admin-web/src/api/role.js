import request from './request'

/** 获取角色列表 */
export function getRoleList() {
  return request.get('/admin/roles')
}

/** 创建角色 */
export function createRole(data) {
  return request.post('/admin/roles', data)
}

/** 更新角色 */
export function updateRole(roleId, data) {
  return request.put(`/admin/roles/${roleId}`, data)
}

/** 删除角色 */
export function deleteRole(roleId) {
  return request.delete(`/admin/roles/${roleId}`)
}
