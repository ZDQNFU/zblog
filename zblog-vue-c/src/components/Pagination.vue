<script setup>
import { computed } from 'vue'

const props = defineProps({
  current: { type: Number, required: true },
  total: { type: Number, required: true },
  pageSize: { type: Number, required: true },
})

const emit = defineEmits(['change'])

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))

const visiblePages = computed(() => {
  const pages = []
  const max = 7
  let start = Math.max(1, props.current - Math.floor(max / 2))
  let end = Math.min(totalPages.value, start + max - 1)
  if (end - start + 1 < max) {
    start = Math.max(1, end - max + 1)
  }
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})
</script>

<template>
  <nav class="pagination" v-if="totalPages > 1">
    <button :disabled="current <= 1" @click="emit('change', current - 1)">
      上一页
    </button>
    <button
      v-for="p in visiblePages"
      :key="p"
      :class="{ active: p === current }"
      @click="emit('change', p)"
    >
      {{ p }}
    </button>
    <button :disabled="current >= totalPages" @click="emit('change', current + 1)">
      下一页
    </button>
  </nav>
</template>

<style scoped>
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin-top: 32px;
}

button {
  padding: 6px 14px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.12s;
}

button:hover:not(:disabled) {
  background: var(--color-bg);
}

button.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
