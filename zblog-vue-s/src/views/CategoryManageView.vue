<script setup>
import { ref, onMounted } from 'vue'
import { fetchCategories, createCategory, updateCategory, deleteCategory } from '@/api/categories'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const categories = ref([])
const loading = ref(false)
const search = ref('')
let searchTimer = null

const dialogVisible = ref(false)
const dialogTitle = ref('新建分类')
const form = ref({ name: '' })
const editingId = ref(null)
const formLoading = ref(false)

async function load() {
  loading.value = true
  try {
    const params = {}
    if (search.value) params.search = search.value
    const { data } = await fetchCategories(params)
    categories.value = data.results || data
  } finally {
    loading.value = false
  }
}

function onSearchChange() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => load(), 300)
}

function openDialog(row) {
  if (row) {
    dialogTitle.value = '编辑分类'
    editingId.value = row.id
    form.value = { name: row.name }
  } else {
    dialogTitle.value = '新建分类'
    editingId.value = null
    form.value = { name: '' }
  }
  dialogVisible.value = true
}

async function handleSave() {
  formLoading.value = true
  try {
    if (editingId.value) {
      await updateCategory(editingId.value, form.value)
      ElMessage.success('更新成功')
    } else {
      await createCategory(form.value)
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
    await ElMessageBox.confirm(`确定删除分类「${row.name}」？`, '确认', { type: 'warning' })
    await deleteCategory(row.id)
    ElMessage.success('已删除')
    load()
  } catch { /* cancelled */ }
}

function formatDate(d) { return d ? new Date(d).toLocaleDateString('zh-CN') : '-' }

onMounted(load)
</script>

<template>
  <div>
    <div class="page-header">
      <h2>分类管理</h2>
      <div class="header-right">
        <el-input
          v-model="search"
          placeholder="搜索分类名称..."
          clearable
          style="width: 240px"
          :prefix-icon="Search"
          @input="onSearchChange"
          @clear="load"
        />
        <el-button type="primary" @click="openDialog()">新建分类</el-button>
      </div>
    </div>

    <el-table :data="categories" v-loading="loading" stripe border style="width:100%">
      <el-table-column prop="name" label="名称" min-width="200" />
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="400px" destroy-on-close>
      <el-form :model="form" label-width="60px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
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
</style>
