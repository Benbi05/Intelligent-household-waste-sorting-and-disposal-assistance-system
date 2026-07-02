/**
 * 验证手机号（中国大陆）
 */
function isPhone(phone) {
  return /^1[3-9]\d{9}$/.test(phone)
}

/**
 * 验证非空
 */
function isNotEmpty(val) {
  return val !== '' && val !== null && val !== undefined
}

/**
 * 验证验证码（4-6 位数字）
 */
function isSmsCode(code) {
  return /^\d{4,6}$/.test(code)
}

module.exports = {
  isPhone,
  isNotEmpty,
  isSmsCode,
}
