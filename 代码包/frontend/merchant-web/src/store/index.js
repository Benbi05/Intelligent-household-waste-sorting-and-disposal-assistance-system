import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, logout as logoutApi, refreshToken as refreshTokenApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('merchant_token') || '')
  const refreshToken = ref(localStorage.getItem('merchant_refresh_token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('merchant_info') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const storeName = computed(() => userInfo.value?.storeName || '')
  const merchantId = computed(() => userInfo.value?.merchantId || 0)
  const area = computed(() => userInfo.value?.area || '')

  async function login(username, password, captchaToken, captchaCode) {
    const res = await loginApi(username, password, captchaToken, captchaCode)
    const data = res.data
    token.value = data.token
    refreshToken.value = data.refreshToken
    userInfo.value = {
      merchantId: data.merchantId,
      storeName: data.storeName,
      area: data.area,
      status: data.status || 'approved',
    }

    localStorage.setItem('merchant_token', data.token)
    localStorage.setItem('merchant_refresh_token', data.refreshToken)
    localStorage.setItem('merchant_info', JSON.stringify(userInfo.value))

    return data
  }

  async function doRefreshToken() {
    const res = await refreshTokenApi(refreshToken.value)
    const data = res.data
    token.value = data.token
    refreshToken.value = data.refreshToken
    localStorage.setItem('merchant_token', data.token)
    localStorage.setItem('merchant_refresh_token', data.refreshToken)
    return data
  }

  async function logout() {
    try {
      await logoutApi()
    } catch (e) {
      // ignore
    }
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    localStorage.removeItem('merchant_token')
    localStorage.removeItem('merchant_refresh_token')
    localStorage.removeItem('merchant_info')
  }

  return { token, refreshToken, userInfo, isLoggedIn, storeName, merchantId, area, login, doRefreshToken, logout }
})
