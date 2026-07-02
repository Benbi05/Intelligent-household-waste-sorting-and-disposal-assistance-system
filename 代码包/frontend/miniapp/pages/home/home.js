const app = getApp()
const { get } = require('../../utils/request')
const { maskPhone, formatTime } = require('../../utils/util')
const { mockGetUserInfo, mockGetPointAccount, mockGetPointRules, mockGetPointRecords } = require('../../mock/data')

Page({
  data: {
    userInfo: {},
    pointBalance: 0,
    todayDate: '',
    recentDeliveries: [],
    loading: true
  },

  onShow() {
    if (!app.checkLogin()) return
    this.fetchData()
  },

  onPullDownRefresh() {
    this.fetchData().then(() => wx.stopPullDownRefresh())
  },

  async fetchData() {
    this.setData({ loading: true })
    const today = new Date()
    this.setData({ todayDate: `${today.getMonth()+1}月${today.getDate()}日` })

    try {
      const [userData, pointData] = await Promise.all([
        get('/user/info').catch(() => mockGetUserInfo()),
        get('/user/point/account').catch(() => mockGetPointAccount()),
      ])
      this.setData({
        userInfo: { nickName: userData.nickName || '刘阿姨' },
        pointBalance: pointData.balance || userData.pointBalance || 2580,
      })
    } catch { this.setData({ pointBalance: 2580 }) }

    // 最近投递
    try {
      const recordData = await get('/user/point/records', { page: 1, size: 3 }).catch(() => mockGetPointRecords(1, 3))
      const colors = [
        { bg: '#E8F8EB', ptsColor: '#67c23a', ptsText: '+10 分', isCorrect: true },
        { bg: '#FFFBEB', ptsColor: '#67c23a', ptsText: '+15 分', isCorrect: true },
        { bg: '#EFF6FF', ptsColor: '#67c23a', ptsText: '+10 分', isCorrect: true },
      ]
      this.setData({
        recentDeliveries: (recordData.records || []).slice(0, 3).map((r, i) => ({
          ...r,
          categoryName: r.description || '垃圾分类投放',
          _time: (r.createTime || '').replace('T', ' ').substring(0, 16),
          _bg: colors[i]?.bg || '#f5f5f5',
          _ptsColor: colors[i]?.ptsColor || '#67c23a',
          _ptsText: colors[i]?.ptsText || `+${r.amount || 0} 分`,
          _isCorrect: r.isCorrect !== undefined ? r.isCorrect : (colors[i]?.isCorrect || true),
        })),
        loading: false,
      })
    } catch {
      this.setData({ recentDeliveries: [], loading: false })
    }
  },

  goRecognize() { wx.navigateTo({ url: '/pages/recognize/recognize' }) },
  goPoints() { wx.navigateTo({ url: '/pages/profile/points' }) },
  goRecords() { wx.navigateTo({ url: '/pages/delivery/list' }) },
  goMall() { wx.switchTab({ url: '/pages/mall/index' }) },
  goReport() { wx.navigateTo({ url: '/pages/report/report' }) },

  maskPhone, formatTime,
})
