<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()

const form = ref({ username: '', password: '', captcha: '' })
const formRef = ref(null)
const lockCountdown = ref(0)
let timer = null

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captcha: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
}

const lockRemainingText = computed(() => {
  if (lockCountdown.value <= 0) return ''
  const m = Math.floor(lockCountdown.value / 60)
  const s = lockCountdown.value % 60
  return `${m} 分 ${s} 秒后可重试`
})

function startLockCountdown(seconds) {
  lockCountdown.value = seconds
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    lockCountdown.value--
    if (lockCountdown.value <= 0) {
      clearInterval(timer)
      timer = null
      auth.loginLocked = 0
    }
  }, 1000)
}

async function handleLogin() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  if (lockCountdown.value > 0) return
  await auth.login(form.value.username, form.value.password, form.value.captcha)
  if (auth.loginLocked > 0) {
    startLockCountdown(auth.loginLocked)
  }
  if (auth.loginError) {
    ElMessage.error(auth.loginError)
  }
}

function refreshCaptcha() {
  auth.loadCaptcha()
}

onMounted(() => {
  auth.loadCaptcha()
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <h2>ZBlog 管理后台</h2>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @keyup.enter="handleLogin">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" size="large" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password size="large" />
        </el-form-item>

        <el-form-item label="验证码" prop="captcha">
          <div class="captcha-row">
            <el-input v-model="form.captcha" placeholder="计算结果" size="large" />
            <div class="captcha-display" @click="refreshCaptcha" title="点击刷新">
              <template v-if="auth.captchaData">
                <span class="captcha-expr">{{ auth.captchaData.expression }}</span>
              </template>
              <span v-else class="captcha-loading">加载中...</span>
            </div>
          </div>
        </el-form-item>

        <p v-if="lockRemainingText" class="lock-tip">
          登录过于频繁，请 {{ lockRemainingText }}
        </p>

        <el-button
          type="primary"
          size="large"
          :loading="auth.isLoggingIn"
          :disabled="lockCountdown > 0"
          class="login-btn"
          @click="handleLogin"
        >
          {{ lockCountdown > 0 ? lockRemainingText : '登 录' }}
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}

.login-card {
  width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-card h2 {
  text-align: center;
  margin-bottom: 28px;
  font-size: 1.3rem;
  color: var(--color-text);
}

.captcha-row {
  display: flex;
  gap: 12px;
  align-items: center;
}
.captcha-row .el-input {
  flex: 1;
}

.captcha-display {
  width: 150px;
  height: 40px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  user-select: none;
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--color-text);
  transition: background 0.2s;
}
.captcha-display:hover {
  background: var(--color-border);
}
.captcha-loading {
  font-size: 0.85rem;
  font-weight: 400;
  color: #999;
}

.lock-tip {
  color: #f56c6c;
  font-size: 0.85rem;
  text-align: center;
  margin-bottom: 8px;
}

.login-btn {
  width: 100%;
  margin-top: 4px;
}
</style>
