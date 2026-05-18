<script setup>
import { ref, reactive, watch, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { sendVerificationCode } from '@/api'

const emit = defineEmits(['close', 'logged-in'])

const auth = useAuthStore()

const tab = ref('login')
const loading = ref(false)
const error = ref('')
const sending = ref(false)
const countdown = ref(0)
let timer = null

const loginForm = reactive({ username: '', password: '', captcha_answer: '' })
const registerForm = reactive({ username: '', email: '', password: '', verification_code: '' })

watch(tab, () => { error.value = '' })

async function loadCaptchaForLogin() {
  await auth.loadCaptcha()
}

// load captcha on mount
loadCaptchaForLogin()

async function handleSendCode() {
  if (!registerForm.email) return
  sending.value = true
  error.value = ''
  try {
    await sendVerificationCode(registerForm.email)
    countdown.value = 60
    timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
        timer = null
      }
    }, 1000)
  } catch (e) {
    error.value = e.message
  } finally {
    sending.value = false
  }
}

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    await auth.login({
      username: loginForm.username,
      password: loginForm.password,
      captcha_key: auth.captchaKey,
      captcha_answer: loginForm.captcha_answer,
    })
    emit('logged-in')
    emit('close')
    resetForms()
  } catch (e) {
    error.value = e.message
    await loadCaptchaForLogin()
    loginForm.captcha_answer = ''
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  loading.value = true
  error.value = ''
  try {
    await auth.register({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      verification_code: registerForm.verification_code,
      verification_key: registerForm.email,
    })
    emit('logged-in')
    emit('close')
    resetForms()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function resetForms() {
  loginForm.username = ''
  loginForm.password = ''
  loginForm.captcha_answer = ''
  registerForm.username = ''
  registerForm.email = ''
  registerForm.password = ''
  registerForm.verification_code = ''
  error.value = ''
}

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="emit('close')">
      <div class="modal-card">
        <button class="modal-close-btn" @click="emit('close')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>

        <div class="tabs">
          <button :class="['tab', { active: tab === 'login' }]" @click="tab = 'login'">登录</button>
          <button :class="['tab', { active: tab === 'register' }]" @click="tab = 'register'">注册</button>
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <!-- Login Form -->
        <form v-if="tab === 'login'" class="form" @submit.prevent="handleLogin">
          <div class="field">
            <label>用户名</label>
            <input v-model="loginForm.username" type="text" required placeholder="请输入用户名" />
          </div>
          <div class="field">
            <label>密码</label>
            <input v-model="loginForm.password" type="password" required placeholder="请输入密码" />
          </div>
          <div class="field captcha-row">
            <label>验证码</label>
            <div class="captcha-group">
              <span class="captcha-expr">{{ auth.captchaExpr }}</span>
              <input v-model="loginForm.captcha_answer" type="text" required placeholder="计算结果" class="captcha-input" />
              <button type="button" class="refresh-captcha" @click="loadCaptchaForLogin" title="刷新验证码">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-1.12-9.36L16 10"/></svg>
              </button>
            </div>
          </div>
          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <!-- Register Form -->
        <form v-else class="form" @submit.prevent="handleRegister">
          <div class="field">
            <label>用户名</label>
            <input v-model="registerForm.username" type="text" required placeholder="请输入用户名" />
          </div>
          <div class="field">
            <label>邮箱</label>
            <div class="captcha-group">
              <input v-model="registerForm.email" type="email" required placeholder="请输入邮箱" />
              <button type="button" class="send-code-btn" :disabled="sending || countdown > 0" @click="handleSendCode">
                {{ countdown > 0 ? `${countdown}s` : sending ? '发送中...' : '发送验证码' }}
              </button>
            </div>
          </div>
          <div class="field">
            <label>验证码</label>
            <input v-model="registerForm.verification_code" type="text" required placeholder="请输入邮箱验证码" />
          </div>
          <div class="field">
            <label>密码</label>
            <input v-model="registerForm.password" type="password" required placeholder="请输入密码（至少6位）" minlength="6" />
          </div>
          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.modal-card {
  position: relative;
  width: 400px;
  max-width: 92vw;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: saturate(180%) blur(16px);
  -webkit-backdrop-filter: saturate(180%) blur(16px);
  border-radius: 16px;
  padding: 32px 28px 24px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.12);
}

.modal-close-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-secondary);
  padding: 4px;
  border-radius: 6px;
  transition: background 0.2s, color 0.2s;
}
.modal-close-btn:hover {
  background: rgba(0, 0, 0, 0.06);
  color: var(--color-text);
}

.tabs {
  display: flex;
  gap: 0;
  margin-bottom: 24px;
  border-bottom: 2px solid var(--color-border);
}
.tab {
  flex: 1;
  padding: 10px;
  border: none;
  background: none;
  font-size: 1rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: color 0.2s, border-color 0.2s;
}
.tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.error-msg {
  background: #fef2f2;
  color: #dc2626;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 0.875rem;
  margin-bottom: 16px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.field label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.field input[type="text"],
.field input[type="password"],
.field input[type="email"] {
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: rgba(255, 255, 255, 0.6);
}
.field input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.captcha-row .captcha-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
.captcha-expr {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text);
  background: #f3f4f6;
  padding: 6px 14px;
  border-radius: 6px;
  user-select: none;
  white-space: nowrap;
}
.captcha-input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  width: 80%;
}
.captcha-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}
.refresh-captcha {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 7px;
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: background 0.2s;
}
.refresh-captcha:hover {
  background: rgba(0, 0, 0, 0.04);
}

.send-code-btn {
  flex-shrink: 0;
  padding: 10px 14px;
  border: 1px solid var(--color-primary);
  border-radius: 8px;
  background: transparent;
  color: var(--color-primary);
  font-size: 0.85rem;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s, color 0.2s;
}
.send-code-btn:hover:not(:disabled) {
  background: var(--color-primary);
  color: #fff;
}
.send-code-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-btn {
  margin-top: 4px;
  padding: 12px;
  border: none;
  border-radius: 10px;
  background: var(--color-primary);
  color: #fff;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.15s;
}
.submit-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}
.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.captcha-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
.captcha-group input {
  flex: 1;
}
</style>
