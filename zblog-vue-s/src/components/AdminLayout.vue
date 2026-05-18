<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const collapsed = ref(false)
const sidebarWidth = computed(() => collapsed.value ? '64px' : '200px')

const baseMenuItems = [
  { path: '/', icon: 'DataAnalysis', label: '首页' },
  { path: '/articles', icon: 'Document', label: '文章管理' },
  { path: '/tags', icon: 'CollectionTag', label: '标签管理' },
  { path: '/categories', icon: 'Folder', label: '分类管理' },
  { path: '/comments', icon: 'ChatLineSquare', label: '评论管理' },
  { path: '/links', icon: 'Link', label: '资源管理' },
  { path: '/chats', icon: 'ChatDotSquare', label: '聊天管理' },
]

const menuItems = computed(() => {
  if (auth.user?.is_superuser) {
    return [...baseMenuItems, { path: '/users', icon: 'User', label: '用户管理' }]
  }
  return baseMenuItems
})

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function toggleSidebar() {
  collapsed.value = !collapsed.value
}

function handleLogout() {
  auth.logout()
}
</script>

<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :style="{ width: sidebarWidth }">
      <div class="sidebar-header">
        <span v-if="!collapsed" class="sidebar-logo">ZBlog</span>
        <span v-else class="sidebar-logo-short">ZB</span>
      </div>
      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          :class="['nav-item', { active: isActive(item.path) }]"
          :title="collapsed ? item.label : ''"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span v-if="!collapsed" class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>
    </aside>

    <!-- Right area: header + content -->
    <div class="main-area">
      <!-- Top header -->
      <header class="top-header">
        <div class="header-left">
          <button class="toggle-btn" @click="toggleSidebar">
            <el-icon :size="20"><Fold v-if="!collapsed" /><Expand v-else /></el-icon>
          </button>
          <span class="header-title">管理后台</span>
        </div>
        <div class="header-right">
          <span class="header-user">{{ auth.user?.username }}</span>
          <button class="logout-btn" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </button>
        </div>
      </header>

      <!-- Main content -->
      <main class="main-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* ---- Sidebar ---- */
.sidebar {
  background: #1d1e2c;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  color: #ccc;
  transition: width 0.25s ease;
  overflow: hidden;
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  text-align: center;
  white-space: nowrap;
}
.sidebar-logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.03em;
}
.sidebar-logo-short {
  font-size: 1.1rem;
  font-weight: 700;
  color: #60a5fa;
}

.sidebar-nav {
  flex: 1;
  padding: 8px 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  font-size: 0.9rem;
  color: #aaa;
  transition: background 0.15s, color 0.15s;
  cursor: pointer;
  white-space: nowrap;
  text-decoration: none;
}
.nav-item:hover {
  background: rgba(255,255,255,0.05);
  color: #ddd;
}
.nav-item.active {
  background: var(--color-primary);
  color: #fff;
}
.nav-label {
  overflow: hidden;
}

/* ---- Main area ---- */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* ---- Top header ---- */
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 52px;
  padding: 0 20px;
  background: #fff;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #606266;
  cursor: pointer;
  transition: background 0.15s;
}
.toggle-btn:hover {
  background: #f0f2f5;
}

.header-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-user {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: #fff;
  color: #606266;
  font-size: 0.85rem;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
}
.logout-btn:hover {
  color: #f56c6c;
  border-color: #f56c6c;
  background: #fef0f0;
}

/* ---- Main content ---- */
.main-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 24px;
  background: var(--color-bg);
}

@media (max-width: 768px) {
  .sidebar {
    width: 64px !important;
  }
  .nav-item { justify-content: center; padding: 12px 0; }
  .sidebar-header { padding: 16px 0; }
  .sidebar-logo-short { display: block; }
  .toggle-btn { display: none; }
  .top-header { padding: 0 12px; }
  .main-content { padding: 16px; }
}

@media (max-width: 480px) {
  .header-user { display: none; }
}
</style>
