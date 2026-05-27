<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, default: '' },
  size: { type: Number, default: 32 },
})

const PALETTE = [
  '#e74c3c', '#e67e22', '#2ecc71', '#1abc9c', '#3498db',
  '#9b59b6', '#e91e63', '#00bcd4', '#ff5722', '#673ab7',
  '#009688', '#f44336', '#3f51b5', '#4caf50', '#795548',
  '#ff6d00', '#00c853', '#2979ff', '#aa00ff', '#c51162',
]

function hash(str) {
  if (!str) return 0
  let h = 0
  for (let i = 0; i < str.length; i++) {
    h = ((h << 5) - h + str.charCodeAt(i)) | 0
  }
  return Math.abs(h)
}

function getInitials(name) {
  if (!name) return '?'
  const trimmed = name.trim()
  // ASCII: take first 1-2 uppercase letters
  if (/^[a-zA-Z]/.test(trimmed)) {
    // Get first letter, optionally second if it's a word boundary
    const parts = trimmed.split(/[\s_-]+/)
    if (parts.length >= 2 && parts[1][0]) {
      return (parts[0][0] + parts[1][0]).toUpperCase()
    }
    return trimmed.slice(0, 2).toUpperCase()
  }
  // Non-ASCII (e.g. Chinese): take first character only
  return trimmed.charAt(0)
}

const color = computed(() => PALETTE[hash(props.name) % PALETTE.length])
const initials = computed(() => getInitials(props.name))

const avatarStyle = computed(() => ({
  width: props.size + 'px',
  height: props.size + 'px',
  fontSize: (props.size * 0.44) + 'px',
  backgroundColor: color.value,
}))
</script>

<template>
  <span class="user-avatar" :style="avatarStyle">{{ initials }}</span>
</template>

<style scoped>
.user-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: #fff;
  font-weight: 700;
  flex-shrink: 0;
  user-select: none;
  line-height: 1;
}
</style>
