<script setup>
import { ref, computed } from 'vue'
import { emojis } from '@/assets/emojis'

defineProps({
  visible: { type: Boolean, default: false },
})
const emit = defineEmits(['select', 'close'])

const search = ref('')
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return emojis
  return emojis.filter(e => e.name.toLowerCase().includes(q))
})
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="emoji-overlay" @click.self="emit('close')">
      <div class="emoji-panel">
        <div class="emoji-header">
          <input
            v-model="search"
            type="text"
            class="emoji-search"
            placeholder="搜索表情..."
            @keydown.escape="emit('close')"
          />
        </div>
        <div class="emoji-grid">
          <button
            v-for="item in filtered"
            :key="item.name"
            class="emoji-item"
            :title="item.name"
            @click="emit('select', item.emoji)"
          >
            {{ item.emoji }}
          </button>
        </div>
        <div v-if="!filtered.length" class="emoji-empty">无匹配表情</div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.emoji-overlay {
  position: fixed;
  inset: 0;
  z-index: 3000;
}

.emoji-panel {
  position: fixed;
  bottom: 120px;
  left: 50%;
  transform: translateX(-50%);
  width: 340px;
  max-height: 320px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.emoji-header {
  padding: 10px 12px;
  border-bottom: 1px solid var(--color-border);
}

.emoji-search {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.85rem;
  background: var(--color-bg);
  color: var(--color-text);
  outline: none;
  transition: border-color 0.2s;
}
.emoji-search:focus {
  border-color: var(--color-primary);
}

.emoji-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 4px;
  padding: 10px;
  overflow-y: auto;
  flex: 1;
}

.emoji-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  aspect-ratio: 1;
  border: none;
  border-radius: 8px;
  background: transparent;
  font-size: 1.4rem;
  cursor: pointer;
  transition: background 0.15s, transform 0.15s;
}
.emoji-item:hover {
  background: var(--color-bg);
  transform: scale(1.3);
}

.emoji-empty {
  padding: 20px;
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 0.85rem;
}
</style>
