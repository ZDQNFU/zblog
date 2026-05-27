import api from './index'

const BASE = '/chat-robot'

export function fetchChatUsers(params = {}) {
  return api.get(`${BASE}/users/`, { params })
}

export function fetchChatUserDetail(userId) {
  return api.get(`${BASE}/users/${userId}/`)
}

export function clearChatHistory(userId) {
  return api.post(`${BASE}/users/${userId}/clear/`)
}

export function trimChatHistory(userId, days) {
  return api.post(`${BASE}/users/${userId}/trim/`, { days })
}
