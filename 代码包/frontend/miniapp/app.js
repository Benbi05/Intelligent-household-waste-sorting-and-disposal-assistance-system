App({
  globalData: {
    userInfo: null,
    token: '',
    refreshToken: '',
    isLoggedIn: false,
    apiBase: 'http://10.242.4.144:8082/api/v1'
  },

  onLaunch() {
    // 恢复登录状态
    const token = wx.getStorageSync('token')
    const refreshToken = wx.getStorageSync('refreshToken')
    const userInfo = wx.getStorageSync('userInfo')
    if (token && userInfo) {
      this.globalData.token = token
      this.globalData.refreshToken = refreshToken
      this.globalData.userInfo = userInfo
      this.globalData.isLoggedIn = true
    }
  },

  checkLogin() {
    if (!this.globalData.isLoggedIn || !this.globalData.token) {
      wx.reLaunch({ url: '/pages/login/login' })
      return false
    }
    return true
  },

  logout() {
    this.globalData.token = ''
    this.globalData.refreshToken = ''
    this.globalData.userInfo = null
    this.globalData.isLoggedIn = false
    wx.removeStorageSync('token')
    wx.removeStorageSync('refreshToken')
    wx.removeStorageSync('userInfo')
    wx.reLaunch({ url: '/pages/login/login' })
  }
})
