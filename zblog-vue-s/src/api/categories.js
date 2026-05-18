import api from './index'

const BASE = '/articles/s/categories'

export function fetchCategories(params = {}) {
  return api.get(`${BASE}/`, { params })
}

export function createCategory(data) {
  return api.post(`${BASE}/`, data)
}

export function updateCategory(id, data) {
  return api.patch(`${BASE}/${id}/`, data)
}

export function deleteCategory(id) {
  return api.delete(`${BASE}/${id}/`)
}
