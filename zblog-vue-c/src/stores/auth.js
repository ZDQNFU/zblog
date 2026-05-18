import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { login as apiLogin, register as apiRegister, fetchCaptcha, fetchUserInfo } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')

  const isAuthenticated = computed(() => !!accessToken.value)

  // captcha state
  const captchaKey = ref('')
  const captchaExpr = ref('')

  async function loadCaptcha() {
    const data = await fetchCaptcha()
    captchaKey.value = data.captcha_key
    captchaExpr.value = data.expression
  }

  function saveAuth(data) {
    user.value = data.user
    accessToken.value = data.access
    refreshToken.value = data.refresh
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    localStorage.setItem('user', JSON.stringify(data.user))
  }

  async function login(credentials) {
    const data = await apiLogin(credentials)
    saveAuth(data)
  }

  async function register(form) {
    const data = await apiRegister(form)
    saveAuth(data)
  }

  async function refreshUser() {
    try {
      const u = await fetchUserInfo()
      user.value = u
      localStorage.setItem('user', JSON.stringify(u))
    } catch {
      // token expired or invalid — ignore
    }
  }

  function logout() {
    user.value = null
    accessToken.value = ''
    refreshToken.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    captchaKey,
    captchaExpr,
    loadCaptcha,
    login,
    register,
    refreshUser,
    logout,
  }
})
