<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>垃圾分类品类管理（{{ total }} 种）</span>
          <el-button type="primary" @click="openDialog()">新增品类</el-button>
        </div>
      </template>

      <!-- 统计卡片 -->
      <el-row :gutter="16" class="stat-row">
        <el-col :span="6"><StatCard label="全部品类" :value="categoryStats.totalCategories || 0" unit="种" color="#1a73e8" /></el-col>
        <el-col :span="6"><StatCard label="可回收物" :value="(categoryStats.byType && categoryStats.byType.recyclable) || 0" unit="种" color="#67c23a" /></el-col>
        <el-col :span="6"><StatCard label="厨余垃圾" :value="(categoryStats.byType && categoryStats.byType.kitchen) || 0" unit="种" color="#ef6c00" /></el-col>
        <el-col :span="6"><StatCard label="有害垃圾" :value="(categoryStats.byType && categoryStats.byType.hazardous) || 0" unit="种" color="#f56c6c" /></el-col>
      </el-row>

      <SearchBar :placeholder="'搜索品类名称'" @search="onSearch" />

      <DataTable :data="list" :loading="loading" action-width="160">
        <el-table-column prop="categoryId" label="编号" width="80" />
        <el-table-column prop="categoryName" label="品类名称" min-width="120" />
        <el-table-column label="大类" width="90">
          <template #default="{ row }">
            <el-tag :type="tagType(row.parentType)" size="small">{{ row.parentTypeName }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="rewardPoint" label="奖励" width="70" />
        <el-table-column prop="penaltyPoint" label="扣除" width="70" />
        <el-table-column label="状态" width="70">
          <template #default="{ row }">
            <StatusTag :status="row.status" />
          </template>
        </el-table-column>
        <template #actions="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.categoryId)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </DataTable>

      <Pagination :total="total" :page="page" :size="size" @change="onPageChange" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑品类' : '新增品类'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="品类名称" prop="categoryName">
          <el-input v-model="form.categoryName" placeholder="如：塑料饮料瓶" />
        </el-form-item>
        <el-form-item label="所属大类" prop="parentType">
          <el-select v-model="form.parentType" @change="onTypeChange">
            <el-option label="可回收物" value="recyclable" />
            <el-option label="厨余垃圾" value="kitchen" />
            <el-option label="有害垃圾" value="hazardous" />
            <el-option label="其他垃圾" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="奖励积分" prop="rewardPoint">
          <el-input-number v-model="form.rewardPoint" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="扣除积分" prop="penaltyPoint">
          <el-input-number v-model="form.penaltyPoint" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="投放指引">
          <el-input v-model="form.guide" type="textarea" placeholder="如：请清空后投入可回收物桶" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.status" active-value="enable" inactive-value="disable" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCategories, createCategory, updateCategory, deleteCategory, getCategoryStats } from '@/api/category'
import DataTable from '@/components/table/DataTable.vue'
import SearchBar from '@/components/search-bar/SearchBar.vue'
import Pagination from '@/components/pagination/Pagination.vue'
import StatusTag from '@/components/status-tag/StatusTag.vue'
import StatCard from '@/components/stat-card/StatCard.vue'

const typeMap = { recyclable: '可回收物', kitchen: '厨余垃圾', hazardous: '有害垃圾', other: '其他垃圾' }

const list = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(20)
const loading = ref(false)
const categoryStats = ref({})
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const formRef = ref(null)
const keyword = ref('')

const form = reactive({
  categoryId: null, categoryName: '', parentType: 'recyclable', parentTypeName: '可回收物',
  rewardPoint: 5, penaltyPoint: 3, guide: '', status: 'enable'
})

const rules = {
  categoryName: [{ required: true, message: '请输入品类名称' }],
  parentType: [{ required: true }],
}

function tagType(type) {
  return { recyclable: 'success', kitchen: 'warning', hazardous: 'danger', other: 'info' }[type] || 'info'
}

function onTypeChange(val) { form.parentTypeName = typeMap[val] || '' }

function onSearch(val) { keyword.value = val; page.value = 1; fetchList() }

function onPageChange(p, s) { page.value = p; size.value = s; fetchList() }

async function fetchList() {
  loading.value = true
  try {
    const res = await getCategories({ page: page.value, size: size.value, keyword: keyword.value })
    list.value = res.data.records; total.value = res.data.total
  } catch { /* handled */ }
  loading.value = false
}

function openDialog(row) {
  if (row) {
    isEdit.value = true
    Object.assign(form, row)
  } else {
    isEdit.value = false
    Object.assign(form, { categoryId: null, categoryName: '', parentType: 'recyclable', parentTypeName: '可回收物', rewardPoint: 5, penaltyPoint: 3, guide: '', status: 'enable' })
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }
  saving.value = true
  try {
    if (isEdit.value) {
      await updateCategory(form.categoryId, form)
      ElMessage.success('更新成功')
    } else {
      await createCategory(form)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchList()
  } catch { /* handled */ }
  saving.value = false
}

async function handleDelete(id) {
  try {
    await deleteCategory(id)
    ElMessage.success('删除成功')
    fetchList()
  } catch { /* handled */ }
}

onMounted(() => { fetchList(); fetchCategoryStats() })

async function fetchCategoryStats() {
  try { const r = await getCategoryStats(); categoryStats.value = r.data } catch {}
}
</script>

<style scoped>
.page-container { padding: 20px; }
.stat-row { margin-bottom: 16px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
