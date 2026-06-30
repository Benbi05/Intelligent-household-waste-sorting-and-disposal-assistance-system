<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">订单管理</h2>
      <el-button type="primary" @click="verifyVisible = true"><el-icon><Checked /></el-icon>扫码核销</el-button>
    </div>

    <div class="page-card">
      <SearchBar v-model="keyword" :show-status="true" :status-options="statusOpts" placeholder="搜索订单ID" @search="fetchList" />
      <DataTable :data="list" :loading="loading">
        <el-table-column prop="orderId" label="订单ID" width="220" show-overflow-tooltip />
        <el-table-column prop="commodityName" label="商品" min-width="130" />
        <el-table-column prop="pointCost" label="积分" width="80" align="center" />
        <el-table-column prop="userPhone" label="用户" width="130" align="center" />
        <el-table-column prop="orderStatus" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.orderStatus==='verified'?'success':row.orderStatus==='cancelled'?'info':'warning'" size="small">
              {{ row.orderStatus==='verified'?'已核销':row.orderStatus==='cancelled'?'已取消':'待核销' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="下单时间" width="170">
          <template #default="{ row }">{{ (row.createTime||'').slice(0,16).replace('T',' ') }}</template>
        </el-table-column>
      </DataTable>
      <Pagination :total="total" v-model:page="page" v-model:size="size" @change="fetchList" />
    </div>

    <!-- 核销弹窗 -->
    <el-dialog v-model="verifyVisible" title="扫码核销" width="400px" :close-on-click-modal="false">
      <div style="text-align:center;padding:16px">
        <div style="font-size:48px;margin-bottom:16px">📱</div>
        <el-input v-model="verifyCode" placeholder="请输入6位核销码" size="large" maxlength="6" style="text-align:center;font-size:20px;letter-spacing:4px" @keyup.enter="handleVerify" />
        <div v-if="verifyResult" :style="{color: verifyResult.ok ? '#2e7d32' : '#c62828', marginTop:'16px', fontSize:'14px', fontWeight:'600'}">
          <template v-if="verifyResult.ok">核销成功！商品：{{ verifyResult.commodityName }}</template>
          <template v-else>{{ verifyResult.msg }}</template>
        </div>
      </div>
      <template #footer>
        <el-button @click="verifyVisible=false;verifyResult=null;verifyCode=''">关闭</el-button>
        <el-button type="primary" :loading="verifying" @click="handleVerify">确认核销</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Checked } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getOrders, verifyOrder } from '@/api/order'
import DataTable from '@/components/table/DataTable.vue'
import SearchBar from '@/components/search-bar/SearchBar.vue'
import Pagination from '@/components/pagination/Pagination.vue'

const list = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const loading = ref(false)
const keyword = reactive({ keyword: '', status: '' })
const statusOpts = [{ label: '待核销', value: 'unverified' }, { label: '已核销', value: 'verified' }, { label: '已取消', value: 'cancelled' }]

const verifyVisible = ref(false)
const verifyCode = ref('')
const verifying = ref(false)
const verifyResult = ref(null)

async function fetchList() {
  loading.value = true
  try {
    const r = await getOrders({ page: page.value, size: size.value, orderStatus: keyword.status })
    list.value = r.data.records || []; total.value = r.data.total || 0
  } catch {}
  loading.value = false
}

async function handleVerify() {
  if (!verifyCode.value || verifyCode.value.length < 6) { ElMessage.warning('请输入正确的6位核销码'); return }
  verifying.value = true
  try {
    const r = await verifyOrder(verifyCode.value)
    verifyResult.value = { ok: true, commodityName: r.data.commodityName }
    verifyCode.value = ''; fetchList()
  } catch (e) { verifyResult.value = { ok: false, msg: e.message || '核销失败' } }
  verifying.value = false
}

fetchList()
</script>

<style scoped>
.page-container { padding: 20px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.page-title { font-size: 20px; font-weight: 700; color: #303133; margin: 0; }
</style>
