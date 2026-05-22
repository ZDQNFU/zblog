<script setup>
import { ref, onMounted, nextTick, watch, onUnmounted } from 'vue'
import { fetchStats } from '@/api/auth'
import { fetchVisitorGeo } from '@/api/tracking'
import { useTheme } from '@/composables/useTheme'
import { Bar, Pie, Doughnut, Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend,
  ArcElement,
} from 'chart.js'
import * as echarts from 'echarts'
import chinaGeoJSON from '@/assets/china.json'

echarts.registerMap('china', chinaGeoJSON)

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend, ArcElement)

const { isDark } = useTheme()

const stats = ref(null)
const loading = ref(false)
const geoData = ref([])
const geoChartRef = ref(null)
let geoChart = null

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
        itemStyle: {
          areaColor: '#409eff33',
        },
        label: {
          show: true,
          color: dark ? '#e2e8f0' : '#333',
        },
      },
      label: {
        show: false,
      },
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
        itemStyle: {
          color: '#f56c6c',
          shadowBlur: 16,
          shadowColor: 'rgba(245,108,108,0.6)',
        },
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
  if (geoData.value.length) {
    initGeoChart()
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' } },
}

onMounted(load)

onUnmounted(() => {
  if (geoChart) {
    geoChart.dispose()
    geoChart = null
  }
})
</script>

<template>
  <div>
    <h2 class="page-title">管理首页</h2>
    <div v-if="loading" class="loading-text">加载中...</div>

    <template v-else-if="stats">

      <!-- 概览卡片 + IP 地图 -->
      <div class="overview-row">
        <div class="overview-stats">
          <h3>数据概览</h3>
          <div class="stat-cards-inner">
            <div class="stat-card">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="#409eff"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8" fill="none" stroke="#409eff" stroke-width="2"/><line x1="16" y1="13" x2="8" y2="13" stroke="#fff" stroke-width="2" stroke-linecap="round"/><line x1="16" y1="17" x2="8" y2="17" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>
              <div class="stat-info"><span class="stat-num">{{ stats.totals.articles }}</span><span class="stat-label">文章总数</span></div>
            </div>
            <div class="stat-card">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="#67c23a"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              <div class="stat-info"><span class="stat-num">{{ stats.totals.published }}</span><span class="stat-label">已发布</span></div>
            </div>
            <div class="stat-card">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="#e6a23c"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
              <div class="stat-info"><span class="stat-num">{{ stats.totals.draft }}</span><span class="stat-label">草稿</span></div>
            </div>
            <div class="stat-card">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="#8b5cf6"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7" stroke="#fff" stroke-width="3" stroke-linecap="round"/></svg>
              <div class="stat-info"><span class="stat-num">{{ stats.totals.tags }}</span><span class="stat-label">标签</span></div>
            </div>
            <div class="stat-card">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="#f56c6c"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
              <div class="stat-info"><span class="stat-num">{{ stats.totals.categories }}</span><span class="stat-label">分类</span></div>
            </div>
            <div class="stat-card">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="#06b6d4"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              <div class="stat-info"><span class="stat-num">{{ stats.totals.comments }}</span><span class="stat-label">评论</span></div>
            </div>
            <div class="stat-card">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="#10b981"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3" fill="#fff"/></svg>
              <div class="stat-info"><span class="stat-num">{{ stats.totals.views }}</span><span class="stat-label">总浏览</span></div>
            </div>
            <div class="stat-card">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="#ef4444"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
              <div class="stat-info"><span class="stat-num">{{ stats.totals.likes }}</span><span class="stat-label">总点赞</span></div>
            </div>
          </div>
        </div>
        <div class="overview-map">
          <h3>访问者 IP 来源分布 ({{ geoData.length }})</h3>
          <div v-if="geoData.length" class="map-container" ref="geoChartRef"></div>
          <div v-else class="map-empty">暂无访问来源数据，请确保已部署 C 端站点并有外部访问</div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-grid">
        <div class="chart-box">
          <h3>文章状态分布</h3>
          <div class="chart-wrapper">
            <Doughnut
              :data="{
                labels: ['已发布', '草稿', '私密'],
                datasets: [{
                  data: [stats.totals.published, stats.totals.draft, stats.totals.private],
                  backgroundColor: ['#67c23a', '#e6a23c', '#f56c6c'],
                }]
              }"
              :options="chartOptions"
            />
          </div>
        </div>

        <div class="chart-box">
          <h3>标签下文章数（Top 10）</h3>
          <div class="chart-wrapper">
            <Bar
              :data="{
                labels: stats.tag_stats.map(t => t.name),
                datasets: [{
                  label: '文章数',
                  data: stats.tag_stats.map(t => t.article_count),
                  backgroundColor: stats.tag_stats.map(t => t.color + '99'),
                  borderColor: stats.tag_stats.map(t => t.color),
                  borderWidth: 1.5,
                  borderRadius: 4,
                }]
              }"
              :options="{ ...chartOptions, plugins: { legend: { display: false } } }"
            />
          </div>
        </div>

        <div class="chart-box">
          <h3>分类文章数</h3>
          <div class="chart-wrapper">
            <Pie
              :data="{
                labels: stats.category_stats.map(c => c.name),
                datasets: [{
                  data: stats.category_stats.map(c => c.article_count),
                  backgroundColor: ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#8b5cf6'],
                }]
              }"
              :options="chartOptions"
            />
          </div>
        </div>

        <div class="chart-box" v-if="stats.monthly_trend?.length">
          <h3>近6月发布趋势</h3>
          <div class="chart-wrapper">
            <Line
              :data="{
                labels: stats.monthly_trend.map(m => m.month?.substring(0, 7)),
                datasets: [{
                  label: '发布数',
                  data: stats.monthly_trend.map(m => m.count),
                  borderColor: '#409eff',
                  backgroundColor: '#409eff33',
                  borderWidth: 2,
                  pointBackgroundColor: '#409eff',
                  pointRadius: 4,
                  fill: true,
                  tension: 0.3,
                }]
              }"
              :options="chartOptions"
            />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.page-title { font-size: 1.4rem; font-weight: 700; margin-bottom: 24px; }
.loading-text { text-align: center; color: var(--color-text-secondary); padding: 80px 0; }

/* ---- Overview row: stats + map ---- */
.overview-row {
  display: flex;
  gap: 20px;
  margin-bottom: 28px;
}

.overview-stats {
  flex: 0 0 380px;
  width: 380px;
  background: var(--color-surface);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.overview-stats h3 { font-size: 0.95rem; margin-bottom: 14px; color: var(--color-text); }

.stat-cards-inner {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--color-bg);
  border-radius: 8px;
  padding: 14px 16px;
  transition: background 0.2s;
}
.stat-card:hover { background: var(--color-border); }

.stat-info { display: flex; flex-direction: column; gap: 2px; }
.stat-num { font-size: 1.35rem; font-weight: 700; color: var(--color-primary); line-height: 1.2; }
.stat-label { font-size: 0.78rem; color: var(--color-text-secondary); }

/* ---- Map ---- */
.overview-map {
  flex: 1;
  min-width: 0;
  background: var(--color-surface);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.overview-map h3 { font-size: 0.95rem; margin-bottom: 14px; color: var(--color-text); }

.map-container { height: 340px; width: 100%; }
.map-empty { height: 340px; display: flex; align-items: center; justify-content: center; color: var(--color-text-secondary); font-size: 0.9rem; }

/* ---- Charts ---- */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}
.chart-box {
  background: var(--color-surface);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.chart-box h3 { font-size: 0.95rem; margin-bottom: 14px; }
.chart-wrapper { height: 260px; position: relative; }

/* ---- Responsive ---- */
@media (max-width: 1024px) {
  .overview-row { flex-direction: column; }
  .overview-stats { flex: none; width: 100%; }
  .stat-cards-inner { grid-template-columns: repeat(4, 1fr); }
  .charts-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .stat-cards-inner { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 480px) {
  .stat-cards-inner { grid-template-columns: 1fr; }
}
</style>
