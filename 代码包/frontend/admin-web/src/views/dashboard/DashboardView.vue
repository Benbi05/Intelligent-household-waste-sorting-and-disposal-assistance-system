<template>
  <div class="dashboard">
    <div class="page-title">{{ roleLabel }}工作台 — {{ community ? community+'社区' : '虎溪街道全部8个社区' }}</div>

    <!-- 指标卡 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6"><StatCard label="本月投放总量" :value="overview.monthDeliveryCount || 0" unit="次" color="#409eff" tip="全社区30天垃圾投放总次数" :trend="overview.deliveryChangeRate || 0" /></el-col>
      <el-col :span="6"><StatCard label="分类正确率" :value="overview.monthCorrectRate ? (overview.monthCorrectRate*100).toFixed(1) : 0" unit="%" color="#67c23a" tip="正确投放占比，达标线85%" :trend="monthTrend" /></el-col>
      <el-col :span="6"><StatCard label="在线设备" :value="overview.onlineDevices || 0" unit="台" color="#e6a23c" tip="正常运行垃圾箱数量" :sub="'待处理 ' + (overview.offlineFaultDevices || 0) + ' 台'" /></el-col>
      <el-col :span="6"><StatCard label="注册用户" :value="overview.totalUsers || 0" unit="人" color="#f56c6c" tip="已注册小程序居民数量" :sub="'本月新增 ' + (overview.newUsersThisMonth || 0) + ' 人'" /></el-col>
    </el-row>

    <!-- 品类正确率 + 环比 -->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>四大类垃圾分类正确率 <span style="font-size:12px;color:#c0c4cc;font-weight:normal">— 厨余垃圾通常最难分</span></template>
          <div class="cat-grid" v-loading="loading">
            <div v-for="c in catData" :key="c.type" class="cat-card" :style="{ borderTopColor: catColor(c.type) }">
              <div class="cat-name">{{ c.name }}</div>
              <div class="cat-rate" :style="{ color: c.rate>=85?'#67c23a':c.rate>=75?'#e6a23c':'#f56c6c' }">{{ c.rate }}%</div>
              <div class="cat-count">正确{{ c.correct }}/共{{ c.total }}次</div>
              <div class="cat-tip">{{ catTip(c) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>本月 vs 上月 <span style="font-size:12px;color:#c0c4cc;font-weight:normal">— 环比变化</span></template>
          <div class="compare-box" v-loading="loading">
            <div class="cmp-row">
              <span class="cmp-label">上月正确率</span>
              <span class="cmp-val">{{ monthCompare.lastMonth?.rate || 0 }}%</span>
            </div>
            <div class="cmp-row">
              <span class="cmp-label">本月正确率</span>
              <span class="cmp-val" :style="{ color: monthCompare.thisMonth?.rate >= 85 ? '#67c23a' : '#f56c6c' }">{{ monthCompare.thisMonth?.rate || 0 }}%</span>
            </div>
            <div class="cmp-arrow">
              变化：<span :style="{ color: compareDelta > 0 ? '#67c23a' : '#f56c6c', fontSize: '22px', fontWeight: '700' }">{{ compareDelta > 0 ? '+' : '' }}{{ compareDelta }}%</span>
              <span v-if="compareDelta > 0" style="color:#67c23a;font-size:14px"> ↑ 持续改善</span>
              <span v-else-if="compareDelta < 0" style="color:#f56c6c;font-size:14px"> ↓ 需关注</span>
              <span v-else style="color:#c0c4cc;font-size:14px"> — 持平</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getOverview } from '@/api/statistics'
import { useUserStore } from '@/store/user'
import StatCard from '@/components/stat-card/StatCard.vue'
import request from '@/api/request'

const userStore = useUserStore()
const roleLabel = computed(() => userStore.role === 'super_admin' ? '物业经理' : '城管监管')
const route = useRoute()
const community = computed(() => route.query.community || '')

const overview = ref({})
const catData = ref([])
const monthCompare = ref({})
const loading = ref(true)

const monthTrend = computed(() => {
  const d = compareDelta.value
  return d > 0 ? Math.abs(d) : d < 0 ? -Math.abs(d) : 0
})

const compareDelta = computed(() => {
  const t = monthCompare.value.thisMonth?.rate || 0
  const l = monthCompare.value.lastMonth?.rate || 0
  return Math.round((t - l) * 10) / 10
})

function catColor(type) {
  return { recyclable: '#409eff', kitchen: '#e6a23c', hazardous: '#f56c6c', other: '#909399' }[type] || '#ccc'
}

function catTip(c) {
  if (c.rate >= 85) return '达标'
  if (c.rate >= 75) return '接近达标，重点宣传'
  return '未达标，需专项整治'
}

const params = computed(() => community.value ? { community: community.value } : {})

async function fetchAll() {
  loading.value = true
  try { const r = await getOverview(params.value); overview.value = r.data } catch {}
  try {
    const [cR, mR] = await Promise.all([
      request.get('/admin/statistics/category-breakdown', { params: params.value }),
      request.get('/admin/statistics/month-compare', { params: params.value }),
    ])
    catData.value = cR.data
    monthCompare.value = mR.data
  } catch {}
  loading.value = false
}

onMounted(fetchAll)
watch(community, fetchAll)
</script>

<style scoped>
.dashboard { padding: 20px; }
.page-title { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 20px; }
.stat-row { margin-bottom: 16px; }

.bar-chart { padding: 10px 0; }
.bar-row { display: flex; align-items: center; margin-bottom: 6px; }
.bar-label { width: 36px; font-size: 12px; color: #606266; text-align: right; margin-right: 8px; flex-shrink: 0; }
.bar-track { flex: 1; height: 18px; background: #f0f2f5; border-radius: 4px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 4px; transition: width .5s; min-width: 2px; }
.bar-val { width: 44px; font-size: 12px; font-weight: 600; text-align: right; margin-left: 8px; flex-shrink: 0; }

.cat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.cat-card { border: 1px solid #ebeef5; border-top: 3px solid #ccc; border-radius: 8px; padding: 14px; text-align: center; }
.cat-name { font-size: 14px; color: #606266; margin-bottom: 8px; font-weight: 500; }
.cat-rate { font-size: 28px; font-weight: 700; margin-bottom: 4px; }
.cat-count { font-size: 12px; color: #c0c4cc; }
.cat-tip { font-size: 12px; margin-top: 6px; color: #909399; }

.compare-box { padding: 16px; }
.cmp-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f0f2f5; }
.cmp-label { font-size: 14px; color: #606266; }
.cmp-val { font-size: 22px; font-weight: 700; }
.cmp-arrow { margin-top: 16px; font-size: 14px; color: #606266; text-align: center; }
</style>
