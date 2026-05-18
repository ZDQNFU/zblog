<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { streamChat, fetchChatHistory } from '@/api'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

const router = useRouter()

const messages = ref([])
const inputText = ref('')
const sending = ref(false)
const chatContainer = ref(null)
const loadingHistory = ref(false)

function addMessage(role, content) {
  messages.value.push({ role, content, id: Date.now() })
}

async function scrollToBottom() {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || sending.value) return

  addMessage('user', text)
  inputText.value = ''
  await scrollToBottom()

  sending.value = true
  const aiId = Date.now()
  messages.value.push({ role: 'ai', content: '', id: aiId })

  streamChat(
    text,
    (token) => {
      const msg = messages.value.find(m => m.id === aiId)
      if (msg) msg.content += token
      scrollToBottom()
    },
    () => {
      sending.value = false
    },
    (err) => {
      const msg = messages.value.find(m => m.id === aiId)
      if (msg) msg.content = `[错误] ${err.message}`
      sending.value = false
      ElMessage.error(err.message || '对话失败')
    }
  )
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

async function loadHistory() {
  loadingHistory.value = true
  try {
    const data = await fetchChatHistory()
    if (data.messages?.length) {
      messages.value = data.messages.map((m, i) => ({ ...m, id: i }))
    } else {
      addMessage('ai', '哼！又来了个烦人的家伙……本小姐今天心情还行，有什么话快说！')
    }
  } catch {
    addMessage('ai', '哼！又来了个烦人的家伙……本小姐今天心情还行，有什么话快说！')
  } finally {
    loadingHistory.value = false
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<template>
  <div class="chat-page">
    <header class="chat-header">
      <el-button :icon="ArrowLeft" text @click="router.push('/')">返回</el-button>
      <h2>明日香 · 聊天</h2>
      <span class="chat-status">在线</span>
    </header>

    <div class="chat-body" ref="chatContainer">
      <div v-if="loadingHistory" class="history-loading">加载聊天记录...</div>
      <div
        v-for="m in messages"
        :key="m.id"
        :class="['message-row', m.role]"
      >
        <div class="message-bubble">
          <div class="message-text">{{ m.content }}</div>
          <div v-if="m.role === 'ai' && sending && m === messages[messages.length - 1]" class="typing-dot">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input-area">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        placeholder="输入消息，Enter 发送，Shift+Enter 换行..."
        :disabled="sending"
        @keydown="handleKeydown"
      />
      <el-button type="primary" :disabled="!inputText.trim() || sending" @click="handleSend">
        发送
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.chat-page {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  z-index: 50;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}
.chat-header h2 {
  flex: 1;
  font-size: 1.1rem;
  font-weight: 600;
}
.chat-status {
  font-size: 0.8rem;
  color: #22c55e;
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-loading {
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 0.85rem;
  padding: 20px;
}

.message-row {
  display: flex;
  max-width: 80%;
}
.message-row.user {
  align-self: flex-end;
}
.message-row.ai {
  align-self: flex-start;
}

.message-bubble {
  padding: 10px 16px;
  border-radius: 12px;
  font-size: 0.9rem;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-word;
}
.message-row.user .message-bubble {
  background: var(--color-primary, #3b82f6);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.message-row.ai .message-bubble {
  background: #fff;
  color: #1f2937;
  border: 1px solid #e5e7eb;
  border-bottom-left-radius: 4px;
}

.typing-dot {
  display: flex;
  gap: 4px;
  margin-top: 6px;
}
.typing-dot span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #9ca3af;
  animation: dot-bounce 1.4s infinite ease-in-out both;
}
.typing-dot span:nth-child(1) { animation-delay: -0.32s; }
.typing-dot span:nth-child(2) { animation-delay: -0.16s; }
.typing-dot span:nth-child(3) { animation-delay: 0s; }

@keyframes dot-bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.chat-input-area {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid #e5e7eb;
  flex-shrink: 0;
}
.chat-input-area .el-textarea {
  flex: 1;
}
.chat-input-area .el-button {
  flex-shrink: 0;
  height: 40px;
}
</style>
