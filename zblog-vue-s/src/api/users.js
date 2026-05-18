import api from './index'

const BASE = '/auth/users'

export function fetchUsers(params = {}) {
  return api.get(`${BASE}/`, { params })
}

export function createUser(data) {
  return api.post(`${BASE}/`, data)
}

export function updateUser(id, data) {
  return api.patch(`${BASE}/${id}/`, data)
}

export function deleteUser(id) {
  return api.delete(`${BASE}/${id}/`)
}
