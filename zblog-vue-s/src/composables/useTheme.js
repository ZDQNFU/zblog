import { ref, computed, watchEffect } from 'vue'

const THEME_KEY = 'zblog-theme'
const theme = ref(localStorage.getItem(THEME_KEY) || 'light')

watchEffect(() => {
  const isDark = theme.value === 'dark'
  document.documentElement.setAttribute('data-theme', theme.value)
  document.documentElement.classList.toggle('dark', isDark)
  localStorage.setItem(THEME_KEY, theme.value)
})

export function useTheme() {
  const isDark = computed(() => theme.value === 'dark')

  function toggle() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }

  return { theme, isDark, toggle }
}
