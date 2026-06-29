import request from './request'

/** 管理员登录 */
export function login(username, password, captchaToken, captchaCode) {
  return request.post('/admin/login', {
    username,
    password,
    captchaToken,
    captchaCode,
  })
}

/** 刷新 token */
export function refreshToken(refreshToken) {
  return request.post('/admin/refresh-token', {}, {
    headers: { 'X-Refresh-Token': refreshToken },
  })
}

/** 退出登录 */
export function logout() {
  return request.post('/admin/logout')
}
