<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  message: { type: Object, required: true },
  color: { type: String, default: '#fff' },
  track: { type: Number, required: true },
  duration: { type: Number, default: 10 },
})

const emit = defineEmits(['done', 'like'])

const auth = useAuthStore()

const prefix = computed(() => props.message.user_name ? `${props.message.user_name}：` : '')
const heart = computed(() => props.message.user_has_liked ? '❤️' : '🤍')

const cardStyle = computed(() => ({
  '--track': props.track,
  '--dur': props.duration + 's',
  backgroundColor: props.color,
}))

function onLike() {
  if (!auth.isAuthenticated) {
    emit('like')
    return
  }
  emit('like', props.message)
}

function onAnimationEnd() {
  emit('done')
}
</script>

<template>
  <div class="dm-card" :style="cardStyle" @animationend="onAnimationEnd">
    <span class="dm-text">{{ prefix }}{{ message.content }}</span>
    <button class="dm-heart" @click.stop="onLike">{{ heart }}</button>
  </div>
</template>

<style scoped>
.dm-card {
  position: absolute;
  top: calc(var(--track) * (100% / 9) + (100% / 9 - 32px) / 2);
  left: 0;
  height: 32px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 1px 3px rgba(0,0,0,0.3);
  white-space: nowrap;
  cursor: default;
  user-select: none;
  padding: 0 14px;
  border-radius: 999px;
  animation: dm-rtl var(--dur) linear forwards;
  animation-play-state: running;
}

.dm-card:hover {
  animation-play-state: paused;
}

.dm-text {
  pointer-events: none;
}

.dm-heart {
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-size: 15px;
  padding: 0;
  transition: transform 0.15s;
  flex-shrink: 0;
}
.dm-heart:hover { transform: scale(1.3); }

@keyframes dm-rtl {
  from { transform: translateX(100vw); }
  to   { transform: translateX(-100%); }
}
</style>
