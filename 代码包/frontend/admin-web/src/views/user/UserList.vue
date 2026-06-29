<template>
  <div class="page-container">
    <h2 class="page-title">用户管理</h2>

    <!-- 搜索栏 -->
    <SearchBar
      v-model="searchForm"
      :show-status="true"
      :status-options="statusOptions"
      @search="onSearch"
      @reset="onReset"
    />

    <!-- 数据表格 -->
    <div class="page-card">
      <DataTable
        :data="tableData"
        :loading="loading"
        :action-width="160"
      >
        <el-table-column prop="userId" label="用户ID" width="80" align="center" />
        <el-table-column prop="nickName" label="昵称" min-width="120" show-overflow-tooltip />
        <el-table-column prop="phone" label="手机号" width="140" align="center" />
        <el-table-column prop="pointBalance" label="积分余额" width="100" align="center" />
        <el-table-column prop="correctRate" label="正确率" width="100" align="center">
          <template #default="{ row }">{{ (row.correctRate * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <StatusTag :status="row.status" />
          </template>
        </el-table-column>
        <el-table-column prop="registerTime" label="注册时间" width="180" align="center">
          <template #default="{ row }">{{ formatTime(row.registerTime) }}</template>
        </el-table-column>

        <template #actions="{ row }">
          <el-button type="primary" link size="small" @click="showDetail(row.userId)">
            详情
          </el-button>
          <el-button
            v-if="row.status === 'enable'"
            type="danger"
            link
            size="small"
            @click="toggleStatus(row, 'disable')"
          >
            禁用
          </el-button>
          <el-button
            v-else
            type="success"
            link
            size="small"
            @click="toggleStatus(row, 'enable')"
          >
            启用
          </el-button>
        </template>
      </DataTable>

      <Pagination
        :total="total"
        v-model:page="pagination.page"
        v-model:size="pagination.size"
        @change="fetchData"
      />
    </div>

    <!-- 用户详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      title="用户详情"
      size="480px"
      @close="detailData = null"
    >
      <div v-if="detailData" class="detail-content">
        <el-descriptions :column="1" border size="default">
          <el-descriptions-item label="用户ID">{{ detailData.userId }}</el-descriptions-item>
          <el-descriptions-item label="昵称">{{ detailData.nickName }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ detailData.phone }}</el-descriptions-item>
          <el-descriptions-item label="积分余额">{{ detailData.pointBalance }}</el-descriptions-item>
          <el-descriptions-item label="累计投递次数">{{ detailData.totalDeliveryTimes }}</el-descriptions-item>
          <el-descriptions-item label="分类正确率">
            {{ (detailData.correctRate * 100).toFixed(1) }}%
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <div v-else v-loading="detailLoading" style="min-height: 200px" />
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getUserList, getUserDetail, updateUserStatus } from '@/api/user'
import DataTable from '@/components/table/DataTable.vue'
import SearchBar from '@/components/search-bar/SearchBar.vue'
import Pagination from '@/components/pagination/Pagination.vue'
import StatusTag from '@/components/status-tag/StatusTag.vue'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)

const searchForm = reactive({ keyword: '', status: '' })
const statusOptions = [
  { label: '启用', value: 'enable' },
  { label: '禁用', value: 'disable' },
]

const pagination = reactive({ page: 1, size: 10 })

// 详情抽屉
const drawerVisible = ref(false)
const detailData = ref(null)
const detailLoading = ref(false)

async function fetchData() {
  loading.value = true
  try {
    const res = await getUserList({
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword,
      status: searchForm.status,
    })
    tableData.value = res.data.records || []
    total.value = res.data.total || 0
  } catch {
    // handled in request interceptor
  } finally {
    loading.value = false
  }
}

function onSearch() {
  pagination.page = 1
  fetchData()
}

function onReset() {
  pagination.page = 1
  fetchData()
}

async function showDetail(userId) {
  drawerVisible.value = true
  detailLoading.value = true
  detailData.value = null
  try {
    const res = await getUserDetail(userId)
    detailData.value = res.data
  } catch {
    drawerVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

async function toggleStatus(row, status) {
  const action = status === 'enable' ? '启用' : '禁用'
  try {
    await ElMessageBox.confirm(`确定要${action}用户「${row.nickName || row.phone}」吗？`, '操作确认', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }

  try {
    await updateUserStatus(row.userId, status)
    ElMessage.success(`${action}成功`)
    fetchData()
  } catch {
    // handled in request interceptor
  }
}

function formatTime(str) {
  if (!str) return '-'
  return str.replace('T', ' ').substring(0, 19)
}

// 初始加载
fetchData()
</script>

<style scoped>
.detail-content {
  padding: 0;
}
</style>
