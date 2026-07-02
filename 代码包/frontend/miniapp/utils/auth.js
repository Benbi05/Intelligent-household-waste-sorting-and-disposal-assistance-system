/**
 * 检查是否已登录
 */
function isLoggedIn() {
  const token = wx.getStorageSync('token')
  return !!token
}

/**
 * 保存登录信息
 */
function saveLogin(data) {
  wx.setStorageSync('token', data.token)
  wx.setStorageSync('refreshToken', data.refreshToken)
  wx.setStorageSync('userInfo', data)
  const app = getApp()
  app.globalData.token = data.token
  app.globalData.refreshToken = data.refreshToken
  app.globalData.userInfo = data
  app.globalData.isLoggedIn = true
}

/**
 * 退出登录
 */
function logout() {
  const { post } = require('./request')
  post('/user/logout').catch(() => {})
  getApp().logout()
}

/**
 * 获取当前用户信息
 */
function getUserInfo() {
  const app = getApp()
  return app.globalData.userInfo || wx.getStorageSync('userInfo')
}

module.exports = {
  isLoggedIn,
  saveLogin,
  logout,
  getUserInfo,
}
