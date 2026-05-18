<script setup>
import { ref, onMounted } from 'vue'
import { fetchLinks, createLink, updateLink, deleteLink } from '@/api/links'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const links = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const search = ref('')
let searchTimer = null

const dialogVisible = ref(false)
const dialogTitle = ref('新建资源')
const form = ref({ name: '', url: '', image_url: '', color: '#3b82f6', description: '' })
const editingId = ref(null)
const formLoading = ref(false)

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (search.value) params.search = search.value
    const { data } = await fetchLinks(params)
    links.value = data.results
    total.value = data.count
  } finally {
    loading.value = false
  }
}

function onSearchChange() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; load() }, 300)
}

function openDialog(row) {
  if (row) {
    dialogTitle.value = '编辑资源'
    editingId.value = row.id
    form.value = {
      name: row.name,
      url: row.url,
      image_url: row.image_url || '',
      color: row.color,
      description: row.description || '',
    }
  } else {
    dialogTitle.value = '新建资源'
    editingId.value = null
    form.value = { name: '', url: '', image_url: '', color: '#3b82f6', description: '' }
  }
  dialogVisible.value = true
}

async function handleSave() {
  formLoading.value = true
  try {
    if (editingId.value) {
      await updateLink(editingId.value, form.value)
      ElMessage.success('更新成功')
    } else {
      await createLink(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    load()
  } catch (e) {
    const detail = e.response?.data?.detail
    const msg = typeof detail === 'string' ? detail : Object.values(e.response?.data || {}).flat().join(', ')
    ElMessage.error(msg || '操作失败')
  } finally {
    formLoading.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除资源「${row.name}」？`, '确认', { type: 'warning' })
    await deleteLink(row.id)
    ElMessage.success('已删除')
    load()
  } catch { /* cancelled */ }
}

function onPageChange(p) { page.value = p; load() }

function formatDate(d) { return d ? new Date(d).toLocaleDateString('zh-CN') : '-' }

onMounted(load)
</script>

<template>
  <div>
    <div class="page-header">
      <h2>资源管理</h2>
      <div class="header-right">
        <el-input
          v-model="search"
          placeholder="搜索资源名称或描述..."
          clearable
          style="width: 240px"
          :prefix-icon="Search"
          @input="onSearchChange"
          @clear="load"
        />
        <el-button type="primary" @click="openDialog()">新建资源</el-button>
      </div>
    </div>

    <el-table :data="links" v-loading="loading" stripe border style="width:100%">
      <el-table-column prop="name" label="名称" min-width="160" />
      <el-table-column label="URL" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">{{ row.url }}</template>
      </el-table-column>
      <el-table-column label="颜色" width="80">
        <template #default="{ row }">
          <div class="color-block" :style="{ background: row.color }"></div>
        </template>
      </el-table-column>
      <el-table-column prop="created_by_name" label="创建人" width="100" />
      <el-table-column label="创建时间" min-width="110">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="最后修改" min-width="110">
        <template #default="{ row }">{{ formatDate(row.updated_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" min-width="140">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-wrap">
      <el-pagination
        background layout="total, prev, pager, next"
        :total="total" :page-size="pageSize" :current-page="page"
        @current-change="onPageChange"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px" destroy-on-close>
      <el-form :model="form" label-width="70px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="资源名称" />
        </el-form-item>
        <el-form-item label="URL">
          <el-input v-model="form.url" placeholder="https://..." />
        </el-form-item>
        <el-form-item label="图片URL">
          <el-input v-model="form.image_url" placeholder="https://... (可选)" />
        </el-form-item>
        <el-form-item label="主题色">
          <el-color-picker v-model="form.color" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="资源简介 (可选)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="formLoading" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; gap: 16px; }
.page-header h2 { font-size: 1.3rem; white-space: nowrap; }
.header-right { display: flex; align-items: center; gap: 12px; }
.pagination-wrap { margin-top: 20px; display: flex; justify-content: center; }
.color-block { width: 24px; height: 24px; border-radius: 4px; margin: 0 auto; }
</style>
