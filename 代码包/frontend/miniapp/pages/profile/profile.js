const app = getApp()
const { get } = require('../../utils/request')
const { maskPhone } = require('../../utils/util')
const { logout } = require('../../utils/auth')
const { mockGetUserInfo, mockGetPointAccount } = require('../../mock/data')

Page({
  data: {
    userInfo: {},
    userStats: {},
    correctRateText: '0.0',
    pointBalance: 0,
  },

  onShow() {
    if (!app.checkLogin()) return
    this.fetchProfile()
  },

  async fetchProfile() {
    try {
      const [userData, pointData] = await Promise.all([
        get('/user/info').catch(() => mockGetUserInfo()),
        get('/user/point/account').catch(() => mockGetPointAccount()),
      ])
      const rate = userData.correctRate || 0
      this.setData({
        userInfo: { nickName: userData.nickName, avatarUrl: userData.avatarUrl, phone: userData.phone },
        userStats: { totalDeliveryTimes: userData.totalDeliveryTimes || 0, correctRate: rate },
        correctRateText: rate ? (rate * 100).toFixed(1) : '0.0',
        pointBalance: pointData.balance || userData.pointBalance || 2580,
      })
    } catch {}
  },

  goPoints() { wx.navigateTo({ url: '/pages/profile/points' }) },
  goDelivery() { wx.navigateTo({ url: '/pages/delivery/list' }) },
  goMall() { wx.navigateTo({ url: '/pages/mall/orders' }) },
  goRecognize() { wx.navigateTo({ url: '/pages/recognize/recognize' }) },
  goReport() { wx.navigateTo({ url: '/pages/report/report' }) },

  handleLogout() {
    wx.showModal({
      title: '退出登录', content: '确定要退出登录吗？',
      success: (res) => { if (res.confirm) logout() }
    })
  },

  maskPhone,
})
