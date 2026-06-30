import request from './request'

/** 获取子账号列表 */
export function getSubAccounts() {
  return request.get('/merchant/sub-accounts')
}

/** 创建子账号 */
export function createSubAccount(data) {
  return request.post('/merchant/sub-accounts', data)
}

/** 删除子账号 */
export function deleteSubAccount(id) {
  return request.delete(`/merchant/sub-accounts/${id}`)
}
