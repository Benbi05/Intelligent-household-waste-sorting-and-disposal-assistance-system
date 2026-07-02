const app = getApp()
const { get } = require('../../utils/request')
const { mockGetPointAccount, mockGetPointRecords } = require('../../mock/data')

Page({
  data: {
    pointBalance: 2580,
    records: [],
    recordFilter: 'all',
    loading: true,
  },

  onLoad() {
    if (!app.checkLogin()) return
    this.fetchData()
  },

  async fetchData() {
    try {
      const [pointData, recordData] = await Promise.all([
        get('/user/point/account').catch(() => mockGetPointAccount()),
        get('/user/point/records', { page: 1, size: 20 }).catch(() => mockGetPointRecords(1, 20)),
      ])
      const formatted = (recordData.records || []).map(r => this.formatRecord(r))
      this._allRecords = formatted
      this.setData({
        pointBalance: pointData.balance || 2580,
        records: formatted,
        loading: false,
      })
    } catch { this.setData({ loading: false }) }
  },

  formatRecord(r) {
    const type = r.recordType || 'earn'
    const amount = r.amount || r.points || 0
    const isPositive = amount >= 0
    const colorMap = { earn: '#67c23a', penalty: '#EF4444', exchange: '#3B82F6', refund: '#F59E0B' }
    const bgMap = { earn: '#E8F8EB', penalty: '#FEF2F2', exchange: '#EFF6FF', refund: '#FFFBEB' }
    const iconMap = { earn: '✅', penalty: '⚠️', exchange: '🎁', refund: '↩️' }
    return {
      ...r, _type: type,
      _color: colorMap[type] || '#67c23a',
      _bgColor: bgMap[type] || '#E8F8EB',
      _icon: iconMap[type] || '✅',
      _sign: isPositive ? '+' : '',
      _time: (r.createTime || '').replace('T', ' ').substring(0, 10),
    }
  },

  onFilterChange(e) {
    const type = e.currentTarget.dataset.type
    const allRecords = this._allRecords || this.data.records
    this.setData({
      recordFilter: type,
      records: type === 'all' ? allRecords : allRecords.filter(r => (r.recordType || 'earn') === type)
    })
  },

  goMall() { wx.switchTab({ url: '/pages/mall/index' }) },
})
