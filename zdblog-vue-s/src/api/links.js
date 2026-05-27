import api from './index'

const BASE = '/links/s/links'

export function fetchLinks(params = {}) {
  return api.get(`${BASE}/`, { params })
}

export function createLink(data) {
  return api.post(`${BASE}/`, data)
}

export function updateLink(id, data) {
  return api.patch(`${BASE}/${id}/`, data)
}

export function fetchLink(id) {
  return api.get(`${BASE}/${id}/`)
}

export function deleteLink(id) {
  return api.delete(`${BASE}/${id}/`)
}
