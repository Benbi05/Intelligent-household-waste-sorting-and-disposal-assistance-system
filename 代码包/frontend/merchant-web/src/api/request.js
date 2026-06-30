import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({ timeout: 15000 })

// 请求拦截器 — 动态检测 API 地址 + 附加 X-Token
service.interceptors.request.use((config) => {
  const host = localStorage.getItem('backend_host')
  if (host) {
    config.url = 'http://' + host + ':8082/api/v1' + config.url
  } else if (window.location.port !== '80' && window.location.port !== '443' && window.location.port !== '') {
    // dev server (8085/5173) or Flask direct (8082) — need /api/v1 prefix
    config.url = 'http://127.0.0.1:8082/api/v1' + config.url
  }

  const token = localStorage.getItem('merchant_token')
  if (token) config.headers['X-Token'] = token
  return config
}, (error) => Promise.reject(error))

// 响应拦截器
let isRefreshing = false
let refreshSubscribers = []

function onRefreshed(newToken) {
  refreshSubscribers.forEach((cb) => cb(newToken))
  refreshSubscribers = []
}

service.interceptors.response.use(
  (response) => {
    const data = response.data
    if (data.code !== 200) {
      ElMessage.error(data.message || '操作失败')
      return Promise.reject(new Error(data.message || '操作失败'))
    }
    return data
  },
  async (error) => {
    if (error.response) {
      const { status, config } = error.response
      if (status === 401 && !config._retry) {
        const refreshToken = localStorage.getItem('merchant_refresh_token')
        if (refreshToken) {
          if (isRefreshing) {
            return new Promise((resolve) => {
              refreshSubscribers.push((newToken) => {
                config.headers['X-Token'] = newToken
                config._retry = true
                resolve(service(config))
              })
            })
          }
          isRefreshing = true
          config._retry = true
          try {
            const host = localStorage.getItem('backend_host')
            let base = host ? 'http://' + host + ':8082/api/v1' : '/api/v1'
            const res = await axios.post(base + '/merchant/refresh-token', {}, {
              headers: { 'X-Refresh-Token': refreshToken },
            })
            if (res.data.code === 200) {
              const { token, refreshToken: newRefresh } = res.data.data
              localStorage.setItem('merchant_token', token)
              localStorage.setItem('merchant_refresh_token', newRefresh)
              onRefreshed(token)
              config.headers['X-Token'] = token
              return service(config)
            }
          } catch (e) {}
          isRefreshing = false
        }
        localStorage.removeItem('merchant_token')
        localStorage.removeItem('merchant_refresh_token')
        localStorage.removeItem('merchant_info')
        window.location.href = '/merchant'
        return Promise.reject(error)
      }
      if (status === 400) {
        const msg = error.response.data?.message || '请求参数错误'
        ElMessage.error(msg)
      } else if (status === 403) {
        ElMessage.error('无权限访问')
      } else if (status >= 500) {
        ElMessage.error('服务器错误')
      }
    } else if (error.message && error.message.includes('timeout')) {
      ElMessage.error('请求超时')
    } else {
      ElMessage.error('网络错误，请确认后端已启动')
    }
    return Promise.reject(error)
  }
)

export default service
