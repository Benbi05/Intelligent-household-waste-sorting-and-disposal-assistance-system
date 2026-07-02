/**
 * 格式化时间
 * @param {string} str - ISO 时间字符串
 */
function formatTime(str) {
  if (!str) return '-'
  return str.replace('T', ' ').substring(0, 19)
}

/**
 * 格式化日期（仅日期部分）
 * @param {string} str - ISO 时间字符串
 */
function formatDate(str) {
  if (!str) return '-'
  return str.substring(0, 10)
}

/**
 * 格式化数字（超过 9999 显示为 1.2w）
 */
function formatNumber(n) {
  if (n >= 10000) return (n / 10000).toFixed(1) + 'w'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k'
  return String(n)
}

/**
 * 手机号脱敏
 */
function maskPhone(phone) {
  if (!phone || phone.length !== 11) return phone || '-'
  return phone.substring(0, 3) + '****' + phone.substring(7)
}

/**
 * 积分变化类型文案
 */
function pointTypeLabel(type) {
  const map = {
    earn: '分类奖励',
    penalty: '违规扣分',
    exchange: '积分兑换',
    refund: '兑换退款',
    activity: '活动奖励',
  }
  return map[type] || type
}

/**
 * 积分变化类型颜色
 */
function pointTypeColor(type) {
  const map = {
    earn: '#67c23a',
    penalty: '#f56c6c',
    exchange: '#409eff',
    refund: '#e6a23c',
    activity: '#67c23a',
  }
  return map[type] || '#909399'
}

module.exports = {
  formatTime,
  formatDate,
  formatNumber,
  maskPhone,
  pointTypeLabel,
  pointTypeColor,
}
