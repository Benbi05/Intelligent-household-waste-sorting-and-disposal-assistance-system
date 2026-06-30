import request from './request'

export function getCategories(params) {
  return request.get('/admin/categories', { params })
}

export function createCategory(data) {
  return request.post('/admin/categories', data)
}

export function updateCategory(id, data) {
  return request.put(`/admin/categories/${id}`, data)
}

export function deleteCategory(id) {
  return request.delete(`/admin/categories/${id}`)
}

/** 获取品类统计概览 */
export function getCategoryStats() {
  return request.get('/admin/categories/stats')
}
