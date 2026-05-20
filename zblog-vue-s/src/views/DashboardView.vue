<script setup>
import { ref, onMounted } from 'vue'
import { fetchStats } from '@/api/auth'
import { Bar, Pie, Doughnut, Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend,
  ArcElement,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend, ArcElement)

const stats = ref(null)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const { data } = await fetchStats()
    stats.value = data
  } finally {
    loading.value = false
  }
}

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' } },
}

onMounted(load)
</script>

<template>
  <div>
    <h2 class="page-title">管理首页</h2>
    <div v-if="loading" class="loading-text">加载中...</div>

    <template v-else-if="stats">
      <!-- 概览卡片 -->
      <div class="stat-cards">
        <div class="stat-card"><span class="stat-num">{{ stats.totals.articles }}</span><span class="stat-label">文章总数</span></div>
        <div class="stat-card"><span class="stat-num">{{ stats.totals.published }}</span><span class="stat-label">已发布</span></div>
        <div class="stat-card"><span class="stat-num">{{ stats.totals.draft }}</span><span class="stat-label">草稿</span></div>
        <div class="stat-card"><span class="stat-num">{{ stats.totals.tags }}</span><span class="stat-label">标签</span></div>
        <div class="stat-card"><span class="stat-num">{{ stats.totals.categories }}</span><span class="stat-label">分类</span></div>
        <div class="stat-card"><span class="stat-num">{{ stats.totals.comments }}</span><span class="stat-label">评论</span></div>
        <div class="stat-card"><span class="stat-num">{{ stats.totals.views }}</span><span class="stat-label">总浏览</span></div>
        <div class="stat-card"><span class="stat-num">{{ stats.totals.likes }}</span><span class="stat-label">总点赞</span></div>
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

.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
  margin-bottom: 28px;
}
.stat-card {
  background: var(--color-surface);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.stat-num { display: block; font-size: 1.8rem; font-weight: 700; color: var(--color-primary); }
.stat-label { font-size: 0.82rem; color: var(--color-text-secondary); }

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
.chart-box-wide { grid-column: span 2; }
.chart-box h3 { font-size: 0.95rem; margin-bottom: 14px; }
.chart-wrapper { height: 260px; position: relative; }

@media (max-width: 1024px) {
  .chart-box-wide { grid-column: span 1; }
  .charts-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .stat-cards { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 480px) {
  .stat-cards { grid-template-columns: 1fr; }
}
</style>
