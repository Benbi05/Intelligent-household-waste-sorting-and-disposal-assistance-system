const { post } = require('../../utils/request')

Page({
  data: { imageUrl: '', result: null },

  // 拍照
  takePhoto() {
    wx.chooseMedia({ count: 1, mediaType: ['image'], sourceType: ['camera'],
      success: (res) => { this.setData({ imageUrl: res.tempFiles[0].tempFilePath }); this.doRecognize(res.tempFiles[0].tempFilePath) }
    })
  },

  // 相册选图
  chooseImage() {
    wx.chooseMedia({ count: 1, mediaType: ['image'], sourceType: ['album'],
      success: (res) => { this.setData({ imageUrl: res.tempFiles[0].tempFilePath }); this.doRecognize(res.tempFiles[0].tempFilePath) }
    })
  },

  // 调识别 API（后端未实现时返回 mock 结果）
  async doRecognize(filePath) {
    // TODO: 后端实现后改为 upload + POST /user/recognize
    // const uploadUrl = await uploadImage(filePath)
    // const result = await post('/user/recognize', { imageUrl: uploadUrl })

    // 演示：随机返回一个分类结果（后端对接后删除此处）
    const results = [
      { categoryName:'塑料瓶', confidence:96, _color:'#3B82F6', _bgColor:'#EFF6FF', _parentName:'可回收物', _tipBg:'#E8F8EB', guide:'请投入蓝色可回收垃圾桶' },
      { categoryName:'废电池', confidence:92, _color:'#EF4444', _bgColor:'#FEF2F2', _parentName:'有害垃圾', _tipBg:'#FEF2F2', guide:'请投入红色有害垃圾桶' },
      { categoryName:'苹果核', confidence:88, _color:'#F59E0B', _bgColor:'#FFFBEB', _parentName:'厨余垃圾', _tipBg:'#FFFBEB', guide:'请投入绿色厨余垃圾桶' },
    ]
    setTimeout(() => this.setData({ result: results[Math.floor(Math.random() * 3)] }), 400)
  },

  confirmDelivery() {
    wx.showToast({ title: '投放成功！+10积分', icon: 'success' })
    setTimeout(() => wx.navigateBack(), 1500)
  },
})
