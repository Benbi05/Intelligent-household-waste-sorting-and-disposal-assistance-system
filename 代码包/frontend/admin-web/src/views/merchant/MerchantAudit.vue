<template>
  <div class="page-container">
    <h2 class="page-title">商家审核</h2>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="8"><StatCard label="待审核" :value="merchantStats.pending || 0" unit="家" color="#e6a23c" /></el-col>
      <el-col :span="8"><StatCard label="已通过" :value="merchantStats.approved || 0" unit="家" color="#67c23a" /></el-col>
      <el-col :span="8"><StatCard label="已拒绝" :value="merchantStats.rejected || 0" unit="家" color="#909399" /></el-col>
    </el-row>

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
      <DataTable :data="tableData" :loading="loading" :action-width="180">
        <el-table-column prop="merchantId" label="商家ID" width="80" align="center" />
        <el-table-column prop="storeName" label="店铺名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="contactName" label="联系人" width="100" align="center" />
        <el-table-column prop="contactPhone" label="联系电话" width="140" align="center" />
        <el-table-column prop="area" label="区域" width="100" align="center" />
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }"><StatusTag :status="row.status" /></template>
        </el-table-column>
        <el-table-column prop="applyTime" label="申请时间" width="170" align="center">
          <template #default="{ row }">{{ formatTime(row.applyTime) }}</template>
        </el-table-column>

        <template #actions="{ row }">
          <template v-if="row.status === 'pending'">
            <el-button type="success" link size="small" @click="audit(row, 'approved')">通过</el-button>
            <el-button type="danger" link size="small" @click="openReject(row)">驳回</el-button>
          </template>
          <span v-else class="tip-text">已处理</span>
        </template>
      </DataTable>

      <Pagination :total="total" v-model:page="pagination.page" v-model:size="pagination.size" @change="fetchList" />
    </div>

    <!-- 驳回理由弹窗 -->
    <el-dialog v-model="rejectVisible" title="驳回商家" width="460px" :close-on-click-modal="false">
      <el-form :model="rejectForm" label-width="80px">
        <el-form-item label="商家名称">{{ rejectForm.storeName }}</el-form-item>
        <el-form-item label="驳回理由">
          <el-input v-model="rejectForm.reason" type="textarea" :rows="3" placeholder="请输入驳回理由" maxlength="256" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="danger" :loading="submitting" @click="handleReject">确定驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getMerchantList, auditMerchant, getMerchantStats } from '@/api/merchant'
import DataTable from '@/components/table/DataTable.vue'
import SearchBar from '@/components/search-bar/SearchBar.vue'
import Pagination from '@/components/pagination/Pagination.vue'
import StatusTag from '@/components/status-tag/StatusTag.vue'
import StatCard from '@/components/stat-card/StatCard.vue'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const submitting = ref(false)
const merchantStats = ref({})

const searchForm = reactive({ keyword: '', status: '' })
const statusOptions = [
  { label: '待审核', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已拒绝', value: 'rejected' },
]

const pagination = reactive({ page: 1, size: 10 })

const rejectVisible = ref(false)
const rejectForm = reactive({ merchantId: null, storeName: '', reason: '' })

async function fetchList() {
  loading.value = true
  try {
    const res = await getMerchantList({
      page: pagination.page, size: pagination.size,
      keyword: searchForm.keyword, status: searchForm.status,
    })
    tableData.value = res.data.records || []
    total.value = res.data.total || 0
  } catch { /* handled */ } finally { loading.value = false }
}

function onSearch() { pagination.page = 1; fetchList() }
function onReset() { pagination.page = 1; fetchList() }

async function audit(row, status) {
  const label = status === 'approved' ? '通过' : '驳回'
  try { await ElMessageBox.confirm(`确定${label}商家「${row.storeName}」的申请吗？`, '审核确认', { type: 'warning' }) } catch { return }
  try {
    await auditMerchant(row.merchantId, { status })
    ElMessage.success(`已${label}`)
    fetchList()
  } catch { /* handled */ }
}

function openReject(row) {
  rejectForm.merchantId = row.merchantId
  rejectForm.storeName = row.storeName
  rejectForm.reason = ''
  rejectVisible.value = true
}

async function handleReject() {
  submitting.value = true
  try {
    await auditMerchant(rejectForm.merchantId, { status: 'rejected', rejectReason: rejectForm.reason })
    ElMessage.success('已驳回')
    rejectVisible.value = false
    fetchList()
  } catch { /* handled */ } finally { submitting.value = false }
}

function formatTime(s) { if (!s) return '-'; return s.replace('T', ' ').substring(0, 19) }

fetchList()
fetchMerchantStats()

async function fetchMerchantStats() {
  try { const r = await getMerchantStats(); merchantStats.value = r.data } catch {}
}
</script>

<style scoped>
.stat-row { margin-bottom: 16px; }
.tip-text { font-size: 13px; color: #c0c4cc; }
</style>
