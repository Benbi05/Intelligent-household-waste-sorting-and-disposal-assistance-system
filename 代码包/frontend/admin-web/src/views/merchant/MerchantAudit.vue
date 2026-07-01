<template>
  <div class="page-container">
    <h2 class="page-title">商家审核</h2>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6"><StatCard label="待审核" :value="merchantStats.pending || 0" unit="家" color="#e6a23c" /></el-col>
      <el-col :span="6"><StatCard label="已通过" :value="merchantStats.approved || 0" unit="家" color="#67c23a" /></el-col>
      <el-col :span="6"><StatCard label="已冻结" :value="merchantStats.frozen || 0" unit="家" color="#409eff" /></el-col>
      <el-col :span="6"><StatCard label="已拒绝" :value="merchantStats.rejected || 0" unit="家" color="#909399" /></el-col>
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
        <el-table-column prop="storeName" label="店铺名称" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <el-button type="primary" link @click="openDetail(row)">{{ row.storeName }}</el-button>
          </template>
        </el-table-column>
        <el-table-column prop="contactName" label="联系人" width="100" align="center" />
        <el-table-column prop="contactPhone" label="联系电话" width="140" align="center" />
        <el-table-column prop="area" label="区域" width="100" align="center" />
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status==='pending'" type="warning" size="small">待审核</el-tag>
            <el-tag v-else-if="row.status==='approved'" type="success" size="small">已通过</el-tag>
            <el-tag v-else-if="row.status==='frozen'" type="info" size="small">已冻结</el-tag>
            <el-tag v-else-if="row.status==='rejected'" type="danger" size="small">已拒绝</el-tag>
            <span v-else>{{ row.status }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="applyTime" label="申请时间" width="170" align="center">
          <template #default="{ row }">{{ formatTime(row.applyTime) }}</template>
        </el-table-column>

        <template #actions="{ row }">
          <template v-if="row.status === 'pending'">
            <el-button type="success" link size="small" @click="audit(row, 'approved')">通过</el-button>
            <el-button type="danger" link size="small" @click="openReject(row)">驳回</el-button>
          </template>
          <template v-else-if="row.status === 'approved'">
            <el-button type="warning" link size="small" @click="handleFreeze(row)">冻结</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">注销</el-button>
          </template>
          <template v-else-if="row.status === 'frozen'">
            <el-button type="primary" link size="small" @click="handleFreeze(row)">解冻</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">注销</el-button>
          </template>
          <span v-else class="tip-text">已拒绝</span>
        </template>
      </DataTable>

      <Pagination :total="total" v-model:page="pagination.page" v-model:size="pagination.size" @change="fetchList" />
    </div>

    <!-- 商家详情弹窗 -->
    <el-dialog v-model="detailVisible" title="商家详情" width="600px" :close-on-click-modal="false">
      <div v-if="detailRow" class="merchant-detail">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="店铺名称" :span="2">{{ detailRow.storeName }}</el-descriptions-item>
          <el-descriptions-item label="登录用户名">{{ detailRow.username }}</el-descriptions-item>
          <el-descriptions-item label="所在社区">{{ detailRow.area }}</el-descriptions-item>
          <el-descriptions-item label="联系人">{{ detailRow.contactName }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ detailRow.contactPhone }}</el-descriptions-item>
          <el-descriptions-item label="店铺地址" :span="2">{{ detailRow.storeAddress || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="状态" :span="2">
            <el-tag v-if="detailRow.status==='pending'" type="warning" size="small">待审核</el-tag>
            <el-tag v-else-if="detailRow.status==='approved'" type="success" size="small">已通过</el-tag>
            <el-tag v-else-if="detailRow.status==='frozen'" type="info" size="small">已冻结</el-tag>
            <el-tag v-else type="danger" size="small">已拒绝</el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <div class="doc-section">
          <div class="doc-title">证照文件</div>
          <el-row :gutter="16">
            <el-col :span="12">
              <div class="doc-label">营业执照</div>
              <div class="doc-img-box">
                <img v-if="detailRow.businessLicense" :src="detailRow.businessLicense" class="doc-img" />
                <span v-else class="doc-empty">未上传</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="doc-label">身份证</div>
              <div class="doc-img-box">
                <img v-if="detailRow.idCard" :src="detailRow.idCard" class="doc-img" />
                <span v-else class="doc-empty">未上传</span>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <template v-if="detailRow && detailRow.status === 'pending'">
          <el-button type="success" @click="detailVisible=false;audit(detailRow,'approved')">通过</el-button>
          <el-button type="danger" @click="detailVisible=false;openReject(detailRow)">驳回</el-button>
        </template>
      </template>
    </el-dialog>

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
import request from '@/api/request'
import DataTable from '@/components/table/DataTable.vue'
import SearchBar from '@/components/search-bar/SearchBar.vue'
import Pagination from '@/components/pagination/Pagination.vue'
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
  { label: '已冻结', value: 'frozen' },
  { label: '已拒绝', value: 'rejected' },
]

const pagination = reactive({ page: 1, size: 10 })

const detailVisible = ref(false)
const detailRow = ref(null)
const rejectVisible = ref(false)
const rejectForm = reactive({ merchantId: null, storeName: '', reason: '' })

function openDetail(row) { detailRow.value = row; detailVisible.value = true }

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

async function handleFreeze(row) {
  const action = row.status === 'frozen' ? '解冻' : '冻结'
  try { await ElMessageBox.confirm(`确定要${action}商家「${row.storeName}」吗？`, '操作确认', { type: 'warning' }) } catch { return }
  try {
    await request.put(`/admin/merchants/${row.merchantId}/freeze`)
    ElMessage.success(action + '成功')
    fetchList()
  } catch {}
}

async function handleDelete(row) {
  try { await ElMessageBox.confirm(`确定要<strong>注销</strong>商家「${row.storeName}」吗？<br/>将删除该商家所有商品、订单数据，不可恢复！`, '危险操作', { type: 'error', dangerouslyUseHTMLString: true, confirmButtonText: '确认注销' }) } catch { return }
  try {
    await request.delete(`/admin/merchants/${row.merchantId}/delete`)
    ElMessage.success('已注销')
    fetchList()
  } catch {}
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
.doc-section { margin-top: 16px; }
.doc-title { font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 10px; }
.doc-label { font-size: 12px; color: #909399; margin-bottom: 6px; }
.doc-img-box { width: 100%; height: 160px; border: 1px dashed #dcdfe6; border-radius: 8px; display: flex; align-items: center; justify-content: center; overflow: hidden; background: #fafbfc; }
.doc-img { width: 100%; height: 100%; object-fit: contain; }
.doc-empty { color: #c0c4cc; font-size: 12px; }
</style>
