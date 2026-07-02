const app = getApp()
const { get } = require('../../utils/request')
const { mockGetPointAccount, mockGetProducts } = require('../../mock/data')

Page({
  data: {
    pointBalance: 2580,
    mallTab: 'all',
    products: [],
  },

  onShow() {
    if (!app.checkLogin()) return
    get('/user/point/account').catch(() => mockGetPointAccount()).then(d => {
      this.setData({ pointBalance: d.balance || 2580 })
    }).catch(() => {})
    this.fetchProducts()
  },

  async fetchProducts() {
    try {
      const data = await get('/mall/products').catch(() => mockGetProducts())
      const list = Array.isArray(data) ? data : (data.records || [])
      this._allProducts = list
      this.applyFilter()
    } catch {}
  },

  setTab(e) {
    this.setData({ mallTab: e.currentTarget.dataset.tab })
    this.applyFilter()
  },

  applyFilter() {
    const tab = this.data.mallTab
    const all = this._allProducts || []
    this.setData({ products: tab === 'all' ? all : all.filter(p => p.cat === tab) })
  },
  goExchange(e) { wx.navigateTo({ url: '/pages/mall/exchange?id=' + e.currentTarget.dataset.id }) },
  goOrders() { wx.navigateTo({ url: '/pages/mall/orders' }) },
})
