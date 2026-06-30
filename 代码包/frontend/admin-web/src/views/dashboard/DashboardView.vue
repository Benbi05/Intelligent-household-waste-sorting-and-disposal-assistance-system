<template>
  <div class="dashboard">
    <div class="page-title">{{ roleLabel }}工作台 — {{ community ? community+'社区' : '虎溪街道全部8个社区' }}</div>

    <!-- 指标卡 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6"><router-link to="/delivery-compare" class="stat-link"><StatCard label="本月投放总量" :value="overview.monthDeliveryCount || 0" unit="次" color="#1a73e8" tip="点击查看各社区投放对比" :trend="overview.deliveryChangeRate || 0" /></router-link></el-col>
      <el-col :span="6"><router-link to="/rate-compare" class="stat-link"><StatCard label="分类正确率" :value="overview.monthCorrectRate ? (overview.monthCorrectRate*100).toFixed(1) : 0" unit="%" color="#2e7d32" tip="点击查看各社区分类正确率" :trend="monthTrend" /></router-link></el-col>
      <el-col :span="6"><router-link to="/device-maintenance" class="stat-link"><StatCard label="在线设备" :value="overview.onlineDevices || 0" unit="台" color="#ef6c00" tip="点击查看待处理设备" :sub="'待处理 ' + (overview.offlineFaultDevices || 0) + ' 台'" /></router-link></el-col>
      <el-col :span="6"><router-link to="/user-stats" class="stat-link"><StatCard label="注册用户" :value="overview.totalUsers || 0" unit="人" color="#78909c" tip="点击查看各社区用户统计" :sub="'本月新增 ' + (overview.newUsersThisMonth || 0) + ' 人'" /></router-link></el-col>
    </el-row>

    <!-- 品类正确率 + 环比 -->
    <el-row :gutter="16" style="margin-top:16px" class="equal-row">
      <el-col :span="12">
        <el-card shadow="never" class="full-card">
          <template #header>四大类垃圾分类正确率 <span style="font-size:12px;color:#c0c4cc;font-weight:normal">— 厨余垃圾通常最难分</span></template>
          <div class="cat-grid" v-loading="loading">
            <div v-for="c in catData" :key="c.type" class="cat-card" :style="{ borderTopColor: catColor(c.type) }">
              <div class="cat-name">{{ c.name }}</div>
              <div class="cat-rate" :style="{ color: c.rate>=85?'#67c23a':c.rate>=75?'#e6a23c':'#f56c6c' }">{{ c.rate }}%</div>
              <div class="cat-count">正确{{ c.correct }}/共{{ c.total }}次</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" class="full-card">
          <template #header>本月 vs 上月 <span style="font-size:12px;color:#c0c4cc;font-weight:normal">— 环比变化</span></template>
          <div class="compare-box" v-loading="loading" style="display:flex;gap:12px;align-items:center;justify-content:center">
            <div ref="pieLastRef" style="width:160px;height:180px"></div>
            <div style="text-align:center;font-size:14px;color:#606266">
              <span v-if="compareDelta > 0" style="color:#67c23a;font-size:20px">▲</span>
              <span v-else-if="compareDelta < 0" style="color:#f56c6c;font-size:20px">▼</span>
              <span v-else style="color:#c0c4cc;font-size:20px">—</span>
              <div :style="{ color: compareDelta > 0 ? '#67c23a' : '#f56c6c', fontSize:'16px', fontWeight:'700', marginTop:'4px' }">{{ compareDelta > 0 ? '+' : '' }}{{ compareDelta }}%</div>
            </div>
            <div ref="pieThisRef" style="width:160px;height:180px"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 各栋对比 + 趋势图（仅单社区视图） -->
    <template v-if="community">
      <el-row :gutter="16" style="margin-top:16px">
        <el-col :span="24">
          <el-card shadow="never">
            <template #header>各栋分类正确率 <span style="font-size:12px;color:#c0c4cc;font-weight:normal">— 红线=达标85%</span></template>
            <div class="bar-chart" v-loading="loading">
              <div v-for="d in bldData" :key="d.building" class="bar-row">
                <span class="bar-label">{{ d.building }}</span>
                <div class="bar-track"><div class="bar-fill" :style="{ width: d.rate+'%', background: d.rate>=85?'#67c23a':d.rate>=80?'#e6a23c':'#f56c6c' }"></div></div>
                <span class="bar-val" :style="{ color: d.rate>=85?'#67c23a':'#f56c6c' }">{{ d.rate }}%</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      <el-row :gutter="16" style="margin-top:16px">
        <el-col :span="24">
          <el-card shadow="never">
            <template #header>近30天投放趋势 <span style="font-size:12px;color:#c0c4cc;font-weight:normal">— 蓝柱=总投放 绿柱=正确 红线=正确率</span></template>
            <div ref="trendChart" style="height:320px" v-loading="loading"></div>
          </el-card>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { getOverview } from '@/api/statistics'
import { useUserStore } from '@/store/user'
import StatCard from '@/components/stat-card/StatCard.vue'
import request from '@/api/request'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.role === 'super_admin')
const roleLabel = computed(() => isAdmin.value ? '物业经理' : '城管监管')
const route = useRoute()
const community = computed(() => route.query.community || '')

const overview = ref({})
const catData = ref([])
const monthCompare = ref({})
const bldData = ref([])
const trdData = ref([])
const trendChart = ref(null)
const pieLastRef = ref(null)
const pieThisRef = ref(null)
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
  return { recyclable: '#1a73e8', kitchen: '#ef6c00', hazardous: '#c62828', other: '#78909c' }[type] || '#78909c'
}

function makePie(el, rate, title) {
  if (!el || !window.echarts) return
  const c = window.echarts.init(el)
  c.setOption({
    title: { text: title, left: 'center', bottom: 0, textStyle: { fontSize: 12, color: '#909399' } },
    series: [{
      type: 'pie', radius: ['50%', '70%'], center: ['50%', '45%'],
      itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.2)', shadowOffsetY: 2 },
      label: { show: true, position: 'center', formatter: '{c}%', fontSize: 18, fontWeight: 'bold', color: rate >= 85 ? '#2e7d32' : rate >= 75 ? '#e65100' : '#c62828' },
      data: [
        { value: rate, name: '正确', itemStyle: { color: rate >= 85 ? '#4caf50' : rate >= 75 ? '#ff9800' : '#ef5350' } },
        { value: 100 - rate, name: '错误', itemStyle: { color: '#eceff1' } }
      ]
    }]
  })
}

function renderPieCharts() {
  const lm = monthCompare.value.lastMonth?.rate || 0
  const tm = monthCompare.value.thisMonth?.rate || 0
  if (pieLastRef.value) makePie(pieLastRef.value, lm, '上月')
  if (pieThisRef.value) makePie(pieThisRef.value, tm, '本月')
}

function catTip(c) { return '' }

const params = computed(() => community.value ? { community: community.value } : {})

async function fetchAll() {
  loading.value = true
  try { const r = await getOverview(params.value); overview.value = r.data } catch {}
  try {
    const apis = [
      request.get('/admin/statistics/category-breakdown', { params: params.value }),
      request.get('/admin/statistics/month-compare', { params: params.value }),
    ]
    if (community.value) {
      apis.push(request.get('/admin/statistics/building-compare', { params: params.value }))
      apis.push(request.get('/admin/statistics/daily-trend', { params: params.value }))
    }
    const results = await Promise.all(apis)
    catData.value = results[0].data
    monthCompare.value = results[1].data
    if (community.value) {
      bldData.value = results[2].data
      trdData.value = results[3].data
      await nextTick()
      renderTrendChart()
    }
  } catch {}
  loading.value = false
  setTimeout(renderPieCharts, 200)
}

onMounted(fetchAll)
watch(community, fetchAll)

function renderTrendChart() {
  if (!trendChart.value || !trdData.value.length) return
  const ec = window.echarts
  if (!ec) return setTimeout(renderTrendChart, 500)
  const chart = ec.init(trendChart.value)
  chart.setOption({
    tooltip: { trigger: 'axis', formatter: p => p[0].axisValue + '<br/>总投放: ' + p[0].value + '次<br/>正确: ' + p[1].value + '次<br/>正确率: ' + (p[1].value/p[0].value*100).toFixed(1) + '%' },
    legend: { data: ['总投放','正确','正确率'], top: 5 },
    grid: { top: 40, right: 60, bottom: 40, left: 50 },
    xAxis: { data: trdData.value.map(d => d.date), axisLabel: { fontSize: 10, rotate: 45, interval: 2 } },
    yAxis: [{ type: 'value', name: '次', axisLabel: { fontSize: 10 } }, { type: 'value', name: '%', min: 0, max: 100, axisLabel: { fontSize: 10, formatter: '{value}%' } }],
    series: [
      { name: '总投放', type: 'bar', data: trdData.value.map(d => d.total), itemStyle: { color: '#409eff', opacity: 0.5 }, barWidth: '40%' },
      { name: '正确', type: 'bar', data: trdData.value.map(d => d.correct), itemStyle: { color: '#67c23a', opacity: 0.8 }, barWidth: '40%' },
      { name: '正确率', type: 'line', yAxisIndex: 1, data: trdData.value.map(d => d.rate), itemStyle: { color: '#f56c6c' }, lineStyle: { width: 2 }, symbol: 'circle', symbolSize: 5, markLine: { silent: true, data: [{ yAxis: 85, label: { formatter: '达标线85%' }, lineStyle: { color: '#f56c6c', type: 'dashed' } }] } }
    ]
  })
}
</script>

<style scoped>
.stat-link { text-decoration: none; color: inherit; display: block; }
.stat-link:hover { opacity: 0.85; transform: translateY(-2px); transition: all .2s; }
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

.equal-row { align-items: stretch; }
.equal-row .el-col { display: flex; }
.equal-row .el-card { flex: 1; width: 100%; }
.compare-box { padding: 0; }
</style>
