<template>
  <div class="dashboard">
    <div class="page-title">商家工作台 — {{ userStore.storeName }}</div>

    <el-row :gutter="16" class="stat-row">
      <el-col :span="6"><StatCard label="上架商品" :value="stats.onCommodities || 0" unit="件" color="#67c23a" /></el-col>
      <el-col :span="6"><StatCard label="本月订单" :value="stats.monthOrders || 0" unit="笔" color="#1a73e8" /></el-col>
      <el-col :span="6"><StatCard label="本月核销" :value="stats.monthVerified || 0" unit="笔" color="#2e7d32" /></el-col>
      <el-col :span="6"><StatCard label="本月积分收入" :value="stats.monthTotalPoints || 0" unit="分" color="#ef6c00" /></el-col>
    </el-row>

    <el-card shadow="never" style="margin-bottom:16px">
      <template #header><span class="section-title">快捷操作</span></template>
      <div class="action-grid">
        <router-link to="/commodities" class="action-item">
          <div class="action-icon" style="background:#67c23a18;color:#67c23a"><el-icon :size="24"><Goods /></el-icon></div>
          <span>商品管理</span>
        </router-link>
        <router-link to="/orders" class="action-item">
          <div class="action-icon" style="background:#1a73e818;color:#1a73e8"><el-icon :size="24"><Document /></el-icon></div>
          <span>订单管理</span>
        </router-link>
        <div class="action-item" @click="verifyVisible = true" style="cursor:pointer">
          <div class="action-icon" style="background:#e6a23c18;color:#e6a23c"><el-icon :size="24"><Checked /></el-icon></div>
          <span>扫码核销</span>
        </div>
      </div>
    </el-card>

    <el-card shadow="never">
      <template #header><span class="section-title">最近订单</span></template>
      <el-table :data="stats.recentOrders || []" size="medium" stripe>
        <el-table-column prop="orderId" label="订单ID" width="220" />
        <el-table-column prop="pointCost" label="积分" width="80" align="center" />
        <el-table-column prop="orderStatus" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.orderStatus==='verified'?'success':row.orderStatus==='cancelled'?'info':'warning'" size="small">
              {{ row.orderStatus==='verified'?'已核销':row.orderStatus==='cancelled'?'已取消':'待核销' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="时间" width="180">
          <template #default="{ row }">{{ (row.createTime||'').slice(0,16).replace('T',' ') }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!stats.recentOrders?.length" description="暂无订单" />
    </el-card>

    <el-dialog v-model="verifyVisible" title="扫码核销" width="400px" :close-on-click-modal="false">
      <div style="text-align:center;padding:16px">
        <div style="font-size:48px;margin-bottom:16px">📱</div>
        <el-input v-model="verifyCode" placeholder="请输入6位核销码" size="large" maxlength="6" style="text-align:center;font-size:20px;letter-spacing:4px" @keyup.enter="handleVerify" />
        <div v-if="verifyResult" :style="{color: verifyResult.ok ? '#2e7d32' : '#c62828', marginTop:'16px', fontSize:'14px', fontWeight:'600'}">
          <template v-if="verifyResult.ok">核销成功！<br/>商品：{{ verifyResult.commodityName }}</template>
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
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store'
import { getMerchantStats } from '@/api/statistics'
import { verifyOrder } from '@/api/order'
import StatCard from '@/components/stat-card/StatCard.vue'
import { Goods, Document, Checked } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const stats = ref({})
const verifyVisible = ref(false)
const verifyCode = ref('')
const verifying = ref(false)
const verifyResult = ref(null)

async function fetchStats() {
  try { const r = await getMerchantStats(); stats.value = r.data } catch {}
}

async function handleVerify() {
  if (!verifyCode.value || verifyCode.value.length < 6) { ElMessage.warning('请输入正确的6位核销码'); return }
  verifying.value = true
  try {
    const r = await verifyOrder(verifyCode.value)
    verifyResult.value = { ok: true, commodityName: r.data.commodityName }
    verifyCode.value = ''
    fetchStats()
  } catch (e) { verifyResult.value = { ok: false, msg: e.message || '核销失败' } }
  verifying.value = false
}

onMounted(fetchStats)
</script>

<style scoped>
.dashboard { padding: 20px; }
.page-title { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 20px; }
.stat-row { margin-bottom: 16px; }
.section-title { font-size: 14px; font-weight: 600; color: #303133; }
.action-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.action-item { display: flex; flex-direction: column; align-items: center; padding: 16px 8px; border-radius: 8px; border: 1px solid #ebeef5; text-decoration: none; color: #303133; transition: all .2s; background: #fafbfc; }
.action-item:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.action-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px; }
</style>
