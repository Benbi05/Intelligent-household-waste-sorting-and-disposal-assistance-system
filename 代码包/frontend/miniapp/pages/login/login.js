const app = getApp()
const { post } = require('../../utils/request')
const { saveLogin } = require('../../utils/auth')

Page({
  data: { loading: false },

  handleWxLogin() {
    this.setData({ loading: true })
    wx.login({
      success: (res) => {
        if (!res.code) {
          wx.showToast({ title: '获取授权码失败', icon: 'none' })
          this.setData({ loading: false })
          return
        }
        post('/user/wx-login', { wxCode: res.code })
          .then(data => {
            saveLogin(data)
            wx.showToast({ title: '登录成功', icon: 'success' })
            setTimeout(() => wx.switchTab({ url: '/pages/home/home' }), 800)
          })
          .catch(() => {
            wx.showToast({ title: '登录失败，请检查网络', icon: 'none' })
            this.setData({ loading: false })
          })
      },
      fail: () => {
        wx.showToast({ title: '微信登录失败', icon: 'none' })
        this.setData({ loading: false })
      }
    })
  },

  onLoad() {
    const token = wx.getStorageSync('token')
    if (token) { wx.switchTab({ url: '/pages/home/home' }) }
  }
})
