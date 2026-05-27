import api from './index'

export function fetchCaptcha() {
  return api.get('/auth/captcha/')
}

export function login(data) {
  return api.post('/auth/login/', data)
}

export function logout(refreshToken) {
  return api.post('/auth/logout/', { refresh: refreshToken })
}

export function fetchUserInfo() {
  return api.get('/auth/me/')
}

export function fetchStats() {
  return api.get('/auth/stats/')
}
