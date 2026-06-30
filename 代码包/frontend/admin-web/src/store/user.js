import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, logout as logoutApi, refreshToken as refreshTokenApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('admin_token') || '')
  const refreshToken = ref(localStorage.getItem('admin_refresh_token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('admin_info') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => userInfo.value?.username || '')
  const role = computed(() => userInfo.value?.role || '')
  const community = computed(() => userInfo.value?.community || '')

  async function login(username, password, captchaToken, captchaCode) {
    const res = await loginApi(username, password, captchaToken, captchaCode)
    const data = res.data
    token.value = data.token
    refreshToken.value = data.refreshToken
    userInfo.value = { adminId: data.adminId, username: data.username, role: data.role, community: data.community || '' }

    localStorage.setItem('admin_token', data.token)
    localStorage.setItem('admin_refresh_token', data.refreshToken)
    localStorage.setItem('admin_info', JSON.stringify(userInfo.value))

    return data
  }

  async function doRefreshToken() {
    const res = await refreshTokenApi(refreshToken.value)
    const data = res.data
    token.value = data.token
    refreshToken.value = data.refreshToken
    localStorage.setItem('admin_token', data.token)
    localStorage.setItem('admin_refresh_token', data.refreshToken)
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
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_refresh_token')
    localStorage.removeItem('admin_info')
  }

  return { token, refreshToken, userInfo, isLoggedIn, username, role, login, doRefreshToken, logout }
})
