Component({
  properties: { title: { type: String, value: '' } },
  data: { statusBarHeight: 20, navBarHeight: 44 },
  lifetimes: {
    attached() {
      const sys = wx.getSystemInfoSync()
      const menu = wx.getMenuButtonBoundingClientRect()
      this.setData({
        statusBarHeight: sys.statusBarHeight,
        navBarHeight: menu.height + (menu.top - sys.statusBarHeight) * 2
      })
    }
  }
})
