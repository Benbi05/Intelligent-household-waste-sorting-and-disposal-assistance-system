const app = getApp()
const { get } = require('../../utils/request')
const { mockGetDeliveryRecords } = require('../../mock/data')

Page({
  data: {
    stats: { count: 28, rate: 92, points: 280 },
    records: [],
    catFilter: 'all',
  },

  onShow() {
    if (!app.checkLogin()) return
    this.fetchRecords()
  },

  async fetchRecords() {
    // 优先调真实 API，失败用 mock
    try {
      const data = await get('/user/delivery/records', { page: 1, size: 50 }).catch(() => mockGetDeliveryRecords())
      const records = Array.isArray(data) ? data : (data.records || [])
      this._allRecords = records
      this.doFilter()
    } catch {}
  },

  onFilter(e) {
    this.setData({ catFilter: e.currentTarget.dataset.type })
    this.doFilter()
  },

  doFilter() {
    const type = this.data.catFilter
    const all = this._allRecords || []
    this.setData({ records: type === 'all' ? all : all.filter(r => r.catType === type) })
  },
})
