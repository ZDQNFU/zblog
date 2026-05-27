import api from './index'

const BASE = '/system-config/s/configs/'

export function fetchConfigs(params) {
  return api.get(BASE, { params })
}

export function createConfig(data) {
  return api.post(BASE, data)
}

export function updateConfig(id, data) {
  return api.patch(`${BASE}${id}/`, data)
}

export function fetchConfig(id) {
  return api.get(`${BASE}${id}/`)
}

export function deleteConfig(id) {
  return api.delete(`${BASE}${id}/`)
}
