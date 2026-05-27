<script setup>
import { ref, onMounted, nextTick, watch, onUnmounted } from 'vue'
import { fetchStats } from '@/api/auth'
import { fetchVisitorGeo } from '@/api/tracking'
import { useTheme } from '@/composables/useTheme'
import { Bar, Pie, Doughnut, Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend,
  ArcElement, Filler,
} from 'chart.js'
import * as echarts from 'echarts'
import chinaGeoJSON from '@/assets/china.json'

echarts.registerMap('china', chinaGeoJSON)

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend, ArcElement, Filler)

const { isDark } = useTheme()

const stats = ref(null)
const loading = ref(false)
const geoData = ref([])
const geoChartRef = ref(null)
let geoChart = null

const countRefs = ref({})

function animateCount(key, target) {
  const el = countRefs.value[key]
  if (!el || target == null) return
  const duration = 900
  const start = performance.now()
  const from = 0
  function step(now) {
    const progress = Math.min((now - start) / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    el.textContent = Math.round(from + eased * (target - from))
    if (progress < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

function triggerCountUp() {
  if (!stats.value) return
  const totals = stats.value.totals
  const keys = ['articles', 'published', 'draft', 'private', 'tags', 'categories', 'comments', 'views', 'likes']
  keys.forEach(k => {
    if (totals[k] != null) animateCount(k, totals[k])
  })
}

watch(stats, (val) => {
  if (val) {
    nextTick(() => triggerCountUp())
  }
})

async function load() {
  loading.value = true
  try {
    const [statsRes, geoRes] = await Promise.all([
      fetchStats(),
      fetchVisitorGeo().catch(() => ({ data: { points: [] } })),
    ])
    stats.value = statsRes.data
    geoData.value = geoRes.data.points || []
  } finally {
    loading.value = false
  }
}

function initGeoChart() {
  if (!geoChartRef.value || !geoData.value.length) return
  if (geoChart) geoChart.dispose()
  geoChart = echarts.init(geoChartRef.value)

  const points = geoData.value.map(p => ({
    value: [p.lon, p.lat],
    name: p.ip,
    city: p.city,
    country: p.country,
  }))

  const dark = isDark.value

  geoChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter(p) {
        if (p.seriesType === 'scatter') {
          const d = p.data
          return `<strong>${d.name}</strong><br/>${d.city}, ${d.country}`
        }
        return p.name
      },
    },
    geo: {
      map: 'china',
      roam: true,
      zoom: 1.2,
      center: [104.5, 36],
      itemStyle: {
        areaColor: dark ? '#1e293b' : '#f0f5ff',
        borderColor: dark ? '#475569' : '#b0c4de',
        borderWidth: 0.5,
      },
      emphasis: {
        itemStyle: { areaColor: '#409eff33' },
        label: { show: true, color: dark ? '#e2e8f0' : '#333' },
      },
      label: { show: false },
    },
    series: [{
      type: 'scatter',
      coordinateSystem: 'geo',
      data: points,
      symbolSize: (val) => Math.min(Math.max(points.length / 2, 6), 14),
      itemStyle: {
        color: '#409eff',
        shadowBlur: 8,
        shadowColor: 'rgba(64,158,255,0.5)',
      },
      emphasis: {
        itemStyle: { color: '#f56c6c', shadowBlur: 16, shadowColor: 'rgba(245,108,108,0.6)' },
      },
    }],
  })
}

watch(geoData, async (val) => {
  if (val.length) {
    await nextTick()
    initGeoChart()
  }
})

watch(isDark, () => {
  if (geoData.value.length) initGeoChart()
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom', labels: { padding: 20, usePointStyle: true, pointStyleWidth: 8 } } },
}

onMounted(load)

onUnmounted(() => {
  if (geoChart) { geoChart.dispose(); geoChart = null }
})

const statCards = [
  { key: 'articles', label: '文章总数', icon: 'articles', color: '#409eff' },
  { key: 'published', label: '已发布', icon: 'published', color: '#22c55e' },
  { key: 'draft', label: '草稿', icon: 'draft', color: '#f59e0b' },
  { key: 'private', label: '私密', icon: 'private', color: '#f56c6c' },
  { key: 'tags', label: '标签', icon: 'tags', color: '#8b5cf6' },
  { key: 'categories', label: '分类', icon: 'categories', color: '#06b6d4' },
  { key: 'comments', label: '评论', icon: 'comments', color: '#ec4899' },
  { key: 'views', label: '总浏览', icon: 'views', color: '#f97316' },
  { key: 'likes', label: '总点赞', icon: 'likes', color: '#ef4444' },
]
</script>

<template>
  <div class="dashboard">
    <h2 class="page-title">管理首页</h2>

    <div v-if="loading" class="loading-skeleton">
      <div v-for="i in 4" :key="i" class="skeleton-card"></div>
    </div>

    <template v-else-if="stats">
      <!-- Stats cards row -->
      <section class="stats-row">
        <div
          v-for="card in statCards"
          :key="card.key"
          class="stat-card"
          :style="{ '--accent': card.color }"
        >
          <div class="stat-icon">
            <!-- Articles -->
            <svg v-if="card.icon === 'articles'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            <!-- Published -->
            <svg v-else-if="card.icon === 'published'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <!-- Draft -->
            <svg v-else-if="card.icon === 'draft'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            <!-- Private -->
            <svg v-else-if="card.icon === 'private'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/><circle cx="12" cy="16" r="1"/></svg>
            <!-- Tags -->
            <svg v-else-if="card.icon === 'tags'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
            <!-- Categories -->
            <svg v-else-if="card.icon === 'categories'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
            <!-- Comments -->
            <svg v-else-if="card.icon === 'comments'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><line x1="8" y1="9" x2="16" y2="9"/><line x1="8" y1="13" x2="14" y2="13"/></svg>
            <!-- Views -->
            <svg v-else-if="card.icon === 'views'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            <!-- Likes -->
            <svg v-else-if="card.icon === 'likes'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
          </div>
          <div class="stat-body">
            <span :ref="el => countRefs[card.key] = el" class="stat-num">0</span>
            <span class="stat-label">{{ card.label }}</span>
          </div>
        </div>
      </section>

      <!-- Map + Status chart row -->
      <section class="dual-row">
        <div class="panel map-panel">
          <h3 class="panel-title">访问者 IP 来源分布 ({{ geoData.length }})</h3>
          <div v-if="geoData.length" class="map-container" ref="geoChartRef"></div>
          <div v-else class="map-empty">暂无访问来源数据</div>
        </div>
        <div class="panel chart-panel">
          <h3 class="panel-title">文章状态分布</h3>
          <div class="chart-wrapper">
            <Doughnut
              :data="{
                labels: ['已发布', '草稿', '私密'],
                datasets: [{
                  data: [stats.totals.published, stats.totals.draft, stats.totals.private],
                  backgroundColor: ['#22c55e', '#f59e0b', '#f56c6c'],
                  borderWidth: 0,
                  borderRadius: 4,
                }]
              }"
              :options="chartOptions"
            />
          </div>
        </div>
      </section>

      <!-- Charts grid -->
      <section class="charts-grid">
        <div class="panel chart-panel">
          <h3 class="panel-title">标签文章数（Top 10）</h3>
          <div class="chart-wrapper">
            <Bar
              :data="{
                labels: stats.tag_stats?.map(t => t.name) || [],
                datasets: [{
                  label: '文章数',
                  data: stats.tag_stats?.map(t => t.article_count) || [],
                  backgroundColor: stats.tag_stats?.map(t => t.color + '99') || [],
                  borderColor: stats.tag_stats?.map(t => t.color) || [],
                  borderWidth: 2,
                  borderRadius: 6,
                  borderSkipped: false,
                }]
              }"
              :options="{ ...chartOptions, plugins: { legend: { display: false } } }"
            />
          </div>
        </div>

        <div class="panel chart-panel">
          <h3 class="panel-title">分类文章数</h3>
          <div class="chart-wrapper">
            <Pie
              :data="{
                labels: stats.category_stats?.map(c => c.name) || [],
                datasets: [{
                  data: stats.category_stats?.map(c => c.article_count) || [],
                  backgroundColor: ['#409eff', '#22c55e', '#f59e0b', '#f56c6c', '#8b5cf6', '#06b6d4', '#ec4899', '#f97316'],
                  borderWidth: 0,
                }]
              }"
              :options="chartOptions"
            />
          </div>
        </div>

        <div class="panel chart-panel" v-if="stats.monthly_trend?.length">
          <h3 class="panel-title">近6月发布趋势</h3>
          <div class="chart-wrapper">
            <Line
              :data="{
                labels: stats.monthly_trend.map(m => m.month?.substring(0, 7)),
                datasets: [{
                  label: '发布数',
                  data: stats.monthly_trend.map(m => m.count),
                  borderColor: '#409eff',
                  backgroundColor: (ctx) => {
                    const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, 260)
                    g.addColorStop(0, 'rgba(64,158,255,0.25)')
                    g.addColorStop(1, 'rgba(64,158,255,0.02)')
                    return g
                  },
                  borderWidth: 2.5,
                  pointBackgroundColor: '#409eff',
                  pointBorderColor: '#fff',
                  pointBorderWidth: 2,
                  pointRadius: 5,
                  pointHoverRadius: 7,
                  fill: true,
                  tension: 0.35,
                }]
              }"
              :options="chartOptions"
            />
          </div>
        </div>

        <div class="panel chart-panel" v-else>
          <h3 class="panel-title">近6月发布趋势</h3>
          <div class="chart-empty">暂无数据</div>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.dashboard { padding-bottom: 32px; }

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 24px;
  color: var(--color-text);
}

/* ========== Loading skeleton ========== */
.loading-skeleton {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.skeleton-card {
  height: 100px;
  border-radius: 12px;
  background: var(--color-surface);
  animation: shimmer 1.5s ease-in-out infinite;
}
@keyframes shimmer {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.85; }
}

/* ========== Stats row ========== */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 14px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--color-surface);
  border-radius: 12px;
  padding: 18px 20px;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  cursor: default;
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}

.stat-icon {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  color: var(--accent);
  flex-shrink: 0;
}

.stat-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.stat-num {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
}
.stat-label {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

/* ========== Panels ========== */
.panel {
  background: var(--color-surface);
  border-radius: 12px;
  padding: 22px 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.panel-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 16px;
}

/* ========== Dual row (map + chart) ========== */
.dual-row {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 20px;
  margin-bottom: 20px;
}

.map-panel {
  min-width: 0;
}
.map-container {
  height: 340px;
  width: 100%;
}
.map-empty {
  height: 340px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  line-height: 1.6;
  text-align: center;
  padding: 0 20px;
}

.chart-wrapper {
  height: 280px;
  position: relative;
}
.chart-empty {
  height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
}

/* ========== Charts grid ========== */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.chart-panel {
  min-width: 0;
}

/* ========== Responsive ========== */
@media (max-width: 1200px) {
  .dual-row {
    grid-template-columns: 1fr;
  }
  .charts-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .chart-wrapper { height: 240px; }
}

@media (max-width: 900px) {
  .stats-row {
    grid-template-columns: repeat(3, 1fr);
  }
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .stat-card { padding: 14px 16px; gap: 10px; }
  .stat-icon { width: 38px; height: 38px; border-radius: 10px; }
  .stat-num { font-size: 1.25rem; }
  .panel { padding: 16px; }
}
</style>
