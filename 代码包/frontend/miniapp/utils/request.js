// 请求基础 URL
const BASE_URL = 'http://10.242.4.144:8082/api/v1'

// 开发模式：后端不可用时设为 true，跳过网络请求直接用 mock 数据
let offlineMode = true

// 是否正在刷新 token
let isRefreshing = false
let refreshCallbacks = []

function isOffline() { return offlineMode }
function setOffline(v) { offlineMode = v }

/**
 * 发起请求
 */
function request(options) {
  // 离线模式：直接拒绝，触发 mock 回退
  if (offlineMode) return Promise.reject(new Error('offline'))

  return new Promise((resolve, reject) => {
    const token = wx.getStorageSync('token')
    const header = { 'Content-Type': 'application/json' }
    if (token) header['X-Token'] = token

    const doRequest = (extraHeaders = {}) => {
      wx.request({
        url: BASE_URL + options.url,
        method: options.method || 'GET',
        data: options.data || {},
        header: { ...header, ...extraHeaders },
        timeout: 5000,
        success(res) {
          const data = res.data
          if (res.statusCode === 200 && data.code === 200) {
            resolve(data.data)
          } else if (res.statusCode === 401 && !options._isRetry) {
            // Token 过期，自动刷新
            handleRefreshToken(() => {
              // 刷新成功后重试
              request({ ...options, _isRetry: true }).then(resolve).catch(reject)
            }, () => {
              // 刷新失败，跳转登录
              reject(new Error('登录已过期'))
            })
          } else {
            wx.showToast({ title: data.message || '操作失败', icon: 'none' })
            reject(data)
          }
        },
        fail(err) {
          wx.showToast({ title: '网络错误，请检查连接', icon: 'none' })
          reject(err)
        }
      })
    }
    doRequest()
  })
}

// Token 刷新
function handleRefreshToken(onSuccess, onFail) {
  const refreshToken = wx.getStorageSync('refreshToken')
  if (!refreshToken) { onFail(); return }

  if (isRefreshing) {
    refreshCallbacks.push(onSuccess)
    return
  }

  isRefreshing = true
  wx.request({
    url: BASE_URL + '/user/refresh-token',
    method: 'POST',
    header: { 'X-Refresh-Token': refreshToken },
    success(res) {
      if (res.data.code === 200) {
        const d = res.data.data
        wx.setStorageSync('token', d.token)
        wx.setStorageSync('refreshToken', d.refreshToken)
        const a = getApp()
        a.globalData.token = d.token
        a.globalData.refreshToken = d.refreshToken
        onSuccess()
        refreshCallbacks.forEach(fn => fn())
      } else {
        clearLoginState()
        onFail()
      }
      refreshCallbacks = []
      isRefreshing = false
    },
    fail() {
      clearLoginState()
      onFail()
      refreshCallbacks = []
      isRefreshing = false
    }
  })
}

function clearLoginState() {
  wx.removeStorageSync('token')
  wx.removeStorageSync('refreshToken')
  wx.removeStorageSync('userInfo')
  const app = getApp()
  app.globalData.token = ''
  app.globalData.isLoggedIn = false
  app.globalData.userInfo = null
  wx.reLaunch({ url: '/pages/login/login' })
}

// 导出常用方法
module.exports = {
  request, isOffline, setOffline,
  get(url, params) { return request({ url, method: 'GET', data: params }) },
  post(url, data) { return request({ url, method: 'POST', data }) },
  put(url, data) { return request({ url, method: 'PUT', data }) },
  del(url, data) { return request({ url, method: 'DELETE', data }) },
}
