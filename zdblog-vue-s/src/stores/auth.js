import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { login as loginApi, logout as logoutApi, fetchCaptcha } from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const loginError = ref('')
  const loginLocked = ref(0) // 剩余锁定秒数
  const captchaData = ref(null)
  const isLoggingIn = ref(false)

  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)

  async function loadCaptcha() {
    try {
      const { data } = await fetchCaptcha()
      captchaData.value = data
    } catch {
      captchaData.value = null
    }
  }

  async function login(username, password, captchaAnswer) {
    isLoggingIn.value = true
    loginError.value = ''
    loginLocked.value = 0
    try {
      const { data } = await loginApi({
        username,
        password,
        captcha_key: captchaData.value?.captcha_key || '',
        captcha_answer: captchaAnswer,
      })
      accessToken.value = data.access
      refreshToken.value = data.refresh
      user.value = data.user
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      localStorage.setItem('user', JSON.stringify(data.user))
      router.push('/')
    } catch (e) {
      const detail = e.response?.data?.detail
      if (e.response?.status === 429 && detail) {
        const match = detail.match(/(\d+)\s*秒/)
        loginLocked.value = match ? parseInt(match[1]) : 60
        loginError.value = detail
      } else {
        const data = e.response?.data
        loginError.value =
          data?.detail ||
          data?.username?.[0] ||
          data?.captcha_answer?.[0] ||
          data?.non_field_errors?.[0] ||
          '登录失败，请重试'
      }
      await loadCaptcha()
    } finally {
      isLoggingIn.value = false
    }
  }

  async function logout() {
    try {
      await logoutApi(refreshToken.value)
    } catch {
      // ignore
    }
    accessToken.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  return { user, accessToken, refreshToken, loginError, loginLocked, captchaData, isLoggingIn, isAuthenticated, loadCaptcha, login, logout }
})
