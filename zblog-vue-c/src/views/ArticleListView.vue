<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchArticleList } from '@/api'
import ArticleCard from '@/components/ArticleCard.vue'
import Pagination from '@/components/Pagination.vue'

const route = useRoute()
const router = useRouter()

const articles = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const error = ref('')

let observer = null

function setupObserver() {
  if (observer) observer.disconnect()
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible')
        }
      })
    },
    { threshold: 0.12 },
  )
  document.querySelectorAll('.fade-up').forEach((el) => observer.observe(el))
}

async function load(page) {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchArticleList(page, pageSize.value)
    articles.value = data.results
    total.value = data.count
    currentPage.value = page
  } catch (e) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
  await nextTick()
  setupObserver()
}

function onPageChange(page) {
  router.push({ query: { page } })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  const p = Number(route.query.page) || 1
  load(p)
})

watch(
  () => route.query.page,
  (newPage) => {
    load(Number(newPage) || 1)
  },
)

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<template>
  <div class="article-list-page container">
    <header class="page-header">
      <h1>文章</h1>
    </header>
    
    <div v-if="loading" class="state-text">加载中...</div>
    <div v-else-if="error" class="state-text error">{{ error }}</div>
    <div v-else-if="!articles.length" class="state-text">暂无文章</div>

    <div v-else class="card-grid">
      <ArticleCard
        v-for="(article, i) in articles"
        :key="article.id"
        :article="article"
        class="fade-up"
        :style="{ transitionDelay: i * 0.08 + 's' }"
      />
    </div>

    <Pagination
      :current="currentPage"
      :total="total"
      :page-size="pageSize"
      @change="onPageChange"
    />
  </div>
</template>

<style scoped>
.article-list-page {
  padding-top: calc(var(--navbar-height) + 32px);
  padding-bottom: 48px;
}

.page-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 24px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.state-text {
  text-align: center;
  color: var(--color-text-secondary);
  padding: 48px 0;
  font-size: 0.95rem;
}
.error { color: #ef4444; }
</style>
