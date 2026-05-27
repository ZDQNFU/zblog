import api from './index'

const BASE = '/messages/s/messages'

export function fetchMessages(params = {}) {
  return api.get(`${BASE}/`, { params })
}

export function createMessage(data) {
  return api.post(`${BASE}/`, data)
}

export function updateMessage(id, data) {
  return api.patch(`${BASE}/${id}/`, data)
}

export function fetchMessage(id) {
  return api.get(`${BASE}/${id}/`)
}

export function deleteMessage(id) {
  return api.delete(`${BASE}/${id}/`)
}
