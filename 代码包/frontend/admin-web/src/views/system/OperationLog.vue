<template>
  <div class="page-container">
    <h2 class="page-title">操作日志</h2>

    <!-- 搜索栏 -->
    <div class="page-card search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="管理员/操作类型" clearable style="width:200px" @keyup.enter="onSearch" @clear="onSearch" />
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="searchForm.actionType" placeholder="全部" clearable style="width:160px" @change="onSearch" @clear="onSearch">
            <el-option label="商家审核" value="merchant_audit" />
            <el-option label="用户管理" value="user_manage" />
            <el-option label="设备管理" value="device_manage" />
            <el-option label="区域管理" value="area_manage" />
            <el-option label="角色管理" value="role_manage" />
            <el-option label="规则发布" value="rule_publish" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始"
            end-placeholder="结束"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width:260px"
            @change="onSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSearch"><el-icon><Search /></el-icon>搜索</el-button>
          <el-button @click="onReset"><el-icon><RefreshRight /></el-icon>重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <div class="page-card">
      <DataTable :data="tableData" :loading="loading">
        <el-table-column prop="logId" label="日志ID" width="80" align="center" />
        <el-table-column prop="adminName" label="操作人" width="110" align="center" />
        <el-table-column prop="actionType" label="操作类型" width="120" align="center">
          <template #default="{ row }"><el-tag size="small">{{ row.actionType }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="targetId" label="目标ID" width="90" align="center" />
        <el-table-column prop="detail" label="操作详情" min-width="250" show-overflow-tooltip />
        <el-table-column prop="ip" label="IP地址" width="150" align="center" />
        <el-table-column prop="createTime" label="操作时间" width="170" align="center">
          <template #default="{ row }">{{ formatTime(row.createTime) }}</template>
        </el-table-column>
      </DataTable>

      <Pagination :total="total" v-model:page="pagination.page" v-model:size="pagination.size" @change="fetchLogs" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Search, RefreshRight } from '@element-plus/icons-vue'
import { getLogList } from '@/api/log'
import DataTable from '@/components/table/DataTable.vue'
import Pagination from '@/components/pagination/Pagination.vue'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)

const searchForm = reactive({ keyword: '', actionType: '' })
const dateRange = ref([])
const pagination = reactive({ page: 1, size: 10 })

async function fetchLogs() {
  loading.value = true
  try {
    const params = {
      page: pagination.page, size: pagination.size,
      keyword: searchForm.keyword, actionType: searchForm.actionType,
    }
    if (dateRange.value && dateRange.value.length === 2) {
      params.startTime = dateRange.value[0]
      params.endTime = dateRange.value[1]
    }
    const res = await getLogList(params)
    tableData.value = res.data.records || []
    total.value = res.data.total || 0
  } catch { /* handled */ } finally { loading.value = false }
}

function onSearch() { pagination.page = 1; fetchLogs() }
function onReset() {
  searchForm.keyword = ''; searchForm.actionType = ''; dateRange.value = []
  pagination.page = 1; fetchLogs()
}

function formatTime(s) { if (!s) return '-'; return s.replace('T', ' ').substring(0, 19) }

fetchLogs()
</script>

<style scoped>
.search-card { margin-bottom: 16px; }
</style>
