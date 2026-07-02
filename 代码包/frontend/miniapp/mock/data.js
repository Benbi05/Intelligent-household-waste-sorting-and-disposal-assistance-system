/**
 * 模拟数据模块
 * 后端对接后，将各函数替换为 utils/request.js 的 API 调用
 * 示例: mockGetUserInfo() → get('/user/info')
 */

// 登录 - 模拟用户数据
function mockLogin() {
  return {
    userId: 1,
    token: 'demo-token-xxxxxxxx',
    refreshToken: 'demo-refresh-xxxxxxxx',
    nickName: '刘阿姨',
    avatarUrl: '',
    phone: '138****1234',
    pointBalance: 320,
  }
}

// GET /user/info
function mockGetUserInfo() {
  return delay({
    userId: 1,
    nickName: '刘阿姨',
    avatarUrl: '',
    phone: '138****1234',
    pointBalance: 320,
    totalDeliveryTimes: 89,
    correctRate: 0.85,
  })
}

// GET /user/point/account
function mockGetPointAccount() {
  return delay({
    balance: 320,
    totalEarned: 1560,
    totalSpent: 1240,
    updateTime: '2026-07-01T10:30:00',
  })
}

// GET /user/point/records?page=&size=&recordType=
function mockGetPointRecords(page = 1, size = 20) {
  const all = [
    { id: 1001, description: '塑料瓶回收', recordType: 'earn', amount: 10, createTime: '2026-07-01T08:30:00' },
    { id: 1002, description: '厨余垃圾投放', recordType: 'earn', amount: 15, createTime: '2026-06-30T19:15:00' },
    { id: 1003, description: '错误分类扣分', recordType: 'penalty', amount: -3, createTime: '2026-06-29T10:00:00' },
    { id: 1004, description: '兑换垃圾袋', recordType: 'exchange', amount: -50, createTime: '2026-06-28T14:20:00' },
    { id: 1005, description: '分类奖励', recordType: 'earn', amount: 10, createTime: '2026-06-27T09:00:00' },
    { id: 1006, description: '厨余投放', recordType: 'earn', amount: 8, createTime: '2026-06-26T18:30:00' },
    { id: 1007, description: '有害垃圾回收', recordType: 'earn', amount: 20, createTime: '2026-06-25T11:00:00' },
    { id: 1008, description: '违规投放罚款', recordType: 'penalty', amount: -5, createTime: '2026-06-24T07:50:00' },
  ]
  return delay({
    records: all.slice((page - 1) * size, page * size),
    total: all.length,
    page,
    size,
  })
}

// GET /user/point/rules
function mockGetPointRules() {
  return delay({
    ruleList: [
      { categoryId: 101, categoryName: '塑料饮料瓶', parentType: 'recyclable', parentTypeName: '可回收物', rewardPoint: 15, penaltyPoint: 5 },
      { categoryId: 102, categoryName: '金属易拉罐', parentType: 'recyclable', parentTypeName: '可回收物', rewardPoint: 12, penaltyPoint: 5 },
      { categoryId: 103, categoryName: '废纸箱', parentType: 'recyclable', parentTypeName: '可回收物', rewardPoint: 10, penaltyPoint: 3 },
      { categoryId: 201, categoryName: '剩饭菜', parentType: 'kitchen', parentTypeName: '厨余垃圾', rewardPoint: 10, penaltyPoint: 5 },
      { categoryId: 202, categoryName: '果皮菜叶', parentType: 'kitchen', parentTypeName: '厨余垃圾', rewardPoint: 12, penaltyPoint: 4 },
      { categoryId: 301, categoryName: '电池', parentType: 'hazardous', parentTypeName: '有害垃圾', rewardPoint: 15, penaltyPoint: 10 },
      { categoryId: 302, categoryName: '过期药品', parentType: 'hazardous', parentTypeName: '有害垃圾', rewardPoint: 20, penaltyPoint: 10 },
      { categoryId: 401, categoryName: '卫生纸', parentType: 'other', parentTypeName: '其他垃圾', rewardPoint: 3, penaltyPoint: 3 },
    ],
  })
}

// 模拟网络延迟
function delay(data, ms = 200) {
  return new Promise(resolve => setTimeout(() => resolve(data), ms))
}

// GET /delivery/records — 投递记录模拟
function mockGetDeliveryRecords() {
  return delay([
    { id:1, description:'塑料瓶回收', isCorrect:true, points:10, _color:'#3B82F6', _ptsColor:'#67c23a', _ptsText:'+10 分', _location:'翠苑小区 #03号垃圾箱', _date:'2026-06-28', catType:'recyclable' },
    { id:2, description:'废纸箱投放', isCorrect:true, points:15, _color:'#3B82F6', _ptsColor:'#67c23a', _ptsText:'+15 分', _location:'翠苑小区 #01号垃圾箱', _date:'2026-06-27', catType:'recyclable' },
    { id:3, description:'废电池回收', isCorrect:true, points:20, _color:'#EF4444', _ptsColor:'#67c23a', _ptsText:'+20 分', _location:'翠苑小区 #05号垃圾箱', _date:'2026-06-25', catType:'hazardous' },
    { id:4, description:'果皮投放', isCorrect:true, points:8, _color:'#F59E0B', _ptsColor:'#67c23a', _ptsText:'+8 分', _location:'翠苑小区 #02号垃圾箱', _date:'2026-06-24', catType:'kitchen' },
    { id:5, description:'一次性餐具投放', isCorrect:false, points:-5, _color:'#6B7280', _ptsColor:'#EF4444', _ptsText:'-5 分', _location:'翠苑小区 #03号垃圾箱', _date:'2026-06-22', catType:'other' },
  ])
}

// GET /mall/products — 积分商城商品模拟
function mockGetProducts() {
  return delay([
    { id:1, name:'环保垃圾袋 卷装', points:200, stock:56, _bg:'#E8F8EB', cat:'daily' },
    { id:2, name:'竹纤维纸巾 3包装', points:350, stock:32, _bg:'#EFF6FF', cat:'daily' },
    { id:3, name:'不锈钢保温杯', points:800, stock:18, _bg:'#FEF2F2', cat:'home' },
    { id:4, name:'环保文具套装', points:300, stock:45, _bg:'#FFFBEB', cat:'gift' },
    { id:5, name:'折叠购物袋', points:150, stock:80, _bg:'#FDF2F8', cat:'daily' },
    { id:6, name:'环保笔记本', points:250, stock:40, _bg:'#E8F8EB', cat:'gift' },
  ])
}

// GET /report — 分析报告模拟
function mockGetReport() {
  return delay({
    catBars: [
      { name:'可回收物', pct:40, color:'#3B82F6' },
      { name:'厨余垃圾', pct:30, color:'#F59E0B' },
      { name:'其他垃圾', pct:20, color:'#6B7280' },
      { name:'有害垃圾', pct:10, color:'#EF4444' },
    ],
    tips: [
      '厨余垃圾分类准确率提升5%，继续保持！',
      '可回收物中塑料瓶占比最高，建议提前分拣',
      '有害垃圾投放较少，请注意电池等小件分类',
    ],
  })
}

module.exports = {
  mockLogin,
  mockGetUserInfo,
  mockGetPointAccount,
  mockGetPointRecords,
  mockGetPointRules,
  mockGetDeliveryRecords,
  mockGetProducts,
  mockGetReport,
}
