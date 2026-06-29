import axios from 'axios'
import { ElMessage } from 'element-plus'

// 自动适配 API 地址
const BACKEND_HOST = localStorage.getItem('backend_host') || window.location.hostname

function getBaseURL() {
  // 同源访问（通过 Flask 提供页面）
  if (window.location.port !== '8084' && window.location.protocol !== 'file:') {
    return '/api/v1'
  }
  // 前端单独跑，指向后端
  return 'http://' + BACKEND_HOST + ':8082/api/v1'
}

const service = axios.create({
  baseURL: getBaseURL(),
  timeout: 15000,
})

// 请求拦截器 — 附加 X-Token
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers['X-Token'] = token
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器 — 统一错误处理 & 401 自动刷新
let isRefreshing = false
let refreshSubscribers = []

function onRefreshed(newToken) {
  refreshSubscribers.forEach((cb) => cb(newToken))
  refreshSubscribers = []
}

function addRefreshSubscriber(cb) {
  refreshSubscribers.push(cb)
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
        const refreshToken = localStorage.getItem('admin_refresh_token')
        if (refreshToken) {
          if (isRefreshing) {
            return new Promise((resolve) => {
              addRefreshSubscriber((newToken) => {
                config.headers['X-Token'] = newToken
                config._retry = true
                resolve(service(config))
              })
            })
          }

          isRefreshing = true
          config._retry = true

          try {
            const res = await axios.post(
              getBaseURL() + '/admin/refresh-token',
              {},
              { headers: { 'X-Refresh-Token': refreshToken } }
            )
            if (res.data.code === 200) {
              const { token, refreshToken: newRefresh } = res.data.data
              localStorage.setItem('admin_token', token)
              localStorage.setItem('admin_refresh_token', newRefresh)
              onRefreshed(token)
              config.headers['X-Token'] = token
              return service(config)
            }
          } catch (e) {
            // 刷新失败，跳登录
          }

          isRefreshing = false
        }

        // 刷新失败或没有 refresh token，清空跳登录
        localStorage.removeItem('admin_token')
        localStorage.removeItem('admin_refresh_token')
        localStorage.removeItem('admin_info')
        window.location.href = '/login'
        return Promise.reject(error)
      }

      if (status === 403) {
        ElMessage.error('无权限访问')
      } else if (status >= 500) {
        ElMessage.error('服务器错误')
      }
    } else if (error.message && error.message.includes('timeout')) {
      ElMessage.error('请求超时，请检查网络')
    } else {
      ElMessage.error('网络错误，请确认后端已启动')
    }
    return Promise.reject(error)
  }
)

export default service
