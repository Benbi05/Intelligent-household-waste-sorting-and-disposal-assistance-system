const BASE_URL = 'http://10.242.4.144:8082/api/v1'

/**
 * 上传图片到后端
 * @param {string} filePath - 本地文件路径
 * @returns {Promise<string>} - 返回图片 URL
 */
function uploadImage(filePath) {
  return new Promise((resolve, reject) => {
    const token = wx.getStorageSync('token')
    wx.uploadFile({
      url: BASE_URL + '/common/upload/image',
      filePath,
      name: 'file',
      header: { 'X-Token': token || '' },
      success(res) {
        try {
          const data = JSON.parse(res.data)
          if (data.code === 200 && data.data && data.data.imageUrl) {
            resolve(data.data.imageUrl)
          } else {
            reject(data)
          }
        } catch {
          reject(new Error('上传失败'))
        }
      },
      fail: reject
    })
  })
}

module.exports = { uploadImage }
