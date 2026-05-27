import api from './index'

const BASE = '/tracking/visitors'

export function fetchVisitors(params = {}) {
  return api.get(`${BASE}/`, { params })
}

export function fetchVisitorDetail(sessionKey) {
  return api.get(`${BASE}/${sessionKey}/`)
}

export function deleteVisitor(sessionKey) {
  return api.delete(`${BASE}/${sessionKey}/`)
}

export function batchDeleteVisitors(sessionKeys) {
  return api.post(`${BASE}/delete/`, { session_keys: sessionKeys })
}

export function fetchVisitorGeo() {
  return api.get(`${BASE}/geo/`)
}
