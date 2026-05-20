<script setup>
import { ref, watch, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue', 'search'])

const inputVal = ref(props.modelValue)
let timer = null

watch(inputVal, (val) => {
  clearTimeout(timer)
  timer = setTimeout(() => {
    emit('update:modelValue', val)
    emit('search', val)
  }, 300)
})

watch(() => props.modelValue, (val) => {
  inputVal.value = val
})

function emitImmediate() {
  clearTimeout(timer)
  emit('update:modelValue', inputVal.value)
  emit('search', inputVal.value)
}

function clearSearch() {
  inputVal.value = ''
  clearTimeout(timer)
  emit('update:modelValue', '')
  emit('search', '')
}

onUnmounted(() => {
  clearTimeout(timer)
})
</script>

<template>
  <div class="search-box">
    <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="11" cy="11" r="8"/>
      <line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>
    <input
      v-model="inputVal"
      type="text"
      class="search-input"
      placeholder="搜索文章..."
      @keydown.enter="emitImmediate"
    />
    <button v-if="inputVal" class="clear-btn" @click="clearSearch">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
  </div>
</template>

<style scoped>
.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 24px;
  padding: 0 16px;
  max-width: 480px;
  margin: 0 auto 24px;
  transition: border-color 0.2s;
}
.search-box:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}
.search-icon {
  color: var(--color-text-secondary);
  flex-shrink: 0;
}
.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: 10px 0;
  font-size: 0.95rem;
  color: var(--color-text);
}
.search-input::placeholder {
  color: var(--color-text-secondary);
  opacity: 0.7;
}
.clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 50%;
  background: var(--color-border);
  color: var(--color-text-secondary);
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s, color 0.15s;
}
.clear-btn:hover {
  background: var(--color-text-secondary);
  color: #fff;
}
</style>
