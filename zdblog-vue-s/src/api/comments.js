import api from './index'

const BASE = '/articles/s/comments'

export function fetchComments(params = {}) {
  return api.get(`${BASE}/`, { params })
}

export function updateComment(id, data) {
  return api.patch(`${BASE}/${id}/`, data)
}

export function fetchComment(id) {
  return api.get(`${BASE}/${id}/`)
}

export function deleteComment(id) {
  return api.delete(`${BASE}/${id}/`)
}
