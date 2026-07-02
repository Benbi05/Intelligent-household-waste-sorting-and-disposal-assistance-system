const app = getApp()
Page({
  data: { orders: [], loading: true },
  onShow() { if (!app.checkLogin()) return; this.setData({ loading: false }) },
})
