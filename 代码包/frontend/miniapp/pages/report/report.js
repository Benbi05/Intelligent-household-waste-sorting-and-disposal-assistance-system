const { get } = require('../../utils/request')
const { mockGetReport } = require('../../mock/data')

Page({
  data: { catBars: [], tips: [] },

  onLoad() {
    get('/user/report').catch(() => mockGetReport()).then(data => {
      this.setData({ catBars: data.catBars || [], tips: data.tips || [] })
    }).catch(() => {})
  },
})
