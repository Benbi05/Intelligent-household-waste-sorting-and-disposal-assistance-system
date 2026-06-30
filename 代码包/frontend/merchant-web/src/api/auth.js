import request from './request'

/** 商家登录 */
export function login(username, password, captchaToken, captchaCode) {
  return request.post('/merchant/login', { username, password, captchaToken, captchaCode })
}

/** 商家入驻申请 */
export function apply(data) {
  return request.post('/merchant/apply', data)
}

/** 刷新 Token */
export function refreshToken(token) {
  return request.post('/merchant/refresh-token', {}, { headers: { 'X-Refresh-Token': token } })
}

/** 登出 */
export function logout() {
  return request.post('/merchant/logout')
}

/** 获取店铺信息 */
export function getShopInfo() {
  return request.get('/merchant/info')
}

/** 更新店铺信息 */
export function updateShopInfo(data) {
  return request.put('/merchant/info', data)
}
