import api from './index'

const BASE = '/articles/s/tags'

export function fetchTags(params = {}) {
  return api.get(`${BASE}/`, { params })
}

export function createTag(data) {
  return api.post(`${BASE}/`, data)
}

export function updateTag(id, data) {
  return api.patch(`${BASE}/${id}/`, data)
}

export function fetchTag(id) {
  return api.get(`${BASE}/${id}/`)
}

export function deleteTag(id) {
  return api.delete(`${BASE}/${id}/`)
}
