<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { createComment } from '@/api'

const props = defineProps({
  articleId: { type: String, required: true },
  replyTo: { type: Object, default: null },
})

const emit = defineEmits(['posted', 'login-request'])

const auth = useAuthStore()
const content = ref('')
const submitting = ref(false)
const error = ref('')

async function handleSubmit() {
  if (!content.value.trim()) return
  submitting.value = true
  error.value = ''
  try {
    const parentId = props.replyTo?.id || null
    await createComment(props.articleId, content.value.trim(), parentId)
    content.value = ''
    emit('posted')
  } catch (e) {
    error.value = e.message
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="comment-form">
    <div v-if="!auth.isAuthenticated" class="login-hint">
      <span>请先登录后发表评论</span>
      <button class="login-trigger-btn" @click="emit('login-request')">登录 / 注册</button>
    </div>

    <template v-else>
      <div v-if="replyTo" class="reply-hint">
        回复 <strong>{{ replyTo.author_name }}</strong>
        <button class="cancel-reply-btn" @click="emit('cancel-reply')">取消回复</button>
      </div>
      <div v-if="error" class="form-error">{{ error }}</div>
      <textarea
        v-model="content"
        class="comment-textarea"
        :placeholder="replyTo ? '写下你的回复...' : '写下你的评论...'"
        rows="3"
      ></textarea>
      <div class="form-actions">
        <span class="form-note">以 <strong>{{ auth.user?.username }}</strong> 的身份发表</span>
        <button class="submit-btn" :disabled="submitting || !content.trim()" @click="handleSubmit">
          {{ submitting ? '提交中...' : '发表评论' }}
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.comment-form {
  margin-bottom: 28px;
  padding: 16px;
  background: var(--color-bg);
  border-radius: 10px;
}

.login-hint {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.login-trigger-btn {
  padding: 6px 18px;
  border: 1px solid var(--color-primary);
  border-radius: 8px;
  background: transparent;
  color: var(--color-primary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.login-trigger-btn:hover {
  background: var(--color-primary);
  color: #fff;
}

.reply-hint {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}
.reply-hint strong {
  color: var(--color-primary);
}
.cancel-reply-btn {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: 0.8rem;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: color 0.2s, background 0.2s;
}
.cancel-reply-btn:hover {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.06);
}

.form-error {
  background: #fef2f2;
  color: #dc2626;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  margin-bottom: 8px;
}

.comment-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.9rem;
  font-family: inherit;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #fff;
}
.comment-textarea:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.form-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
}

.form-note {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

.submit-btn {
  padding: 8px 22px;
  border: none;
  border-radius: 8px;
  background: var(--color-primary);
  color: #fff;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.15s;
}
.submit-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}
.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
