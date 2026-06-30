<template>
  <div class="dashboard">
    <div class="page-title">{{ roleLabel }}工作台 — 虎溪花园社区</div>
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6"><StatCard label="本月投放总量" :value="overview.monthDeliveryCount || 0" unit="次" color="#409eff" tip="全社区30天垃圾投放总次数" /></el-col>
      <el-col :span="6"><StatCard label="分类正确率" :value="overview.monthCorrectRate ? (overview.monthCorrectRate*100).toFixed(1) : 0" unit="%" color="#67c23a" tip="正确投放占比，达标线85%" /></el-col>
      <el-col :span="6"><StatCard label="在线设备" :value="overview.onlineDevices || 0" :unit="'/' + (overview.totalDevices || 0) + '台'" color="#e6a23c" tip="正常运行垃圾箱 / 总数" /></el-col>
      <el-col :span="6"><StatCard label="注册用户" :value="overview.totalUsers || 0" unit="人" color="#f56c6c" tip="已注册小程序居民数量" /></el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="24">
        <el-card shadow="never">
          <template #header>各栋分类正确率 <span style="font-size:12px;color:#c0c4cc;font-weight:normal">— 红线=达标85%</span></template>
          <div class="bar-chart" v-loading="loading">
            <div v-for="d in bldData" :key="d.building" class="bar-row">
              <span class="bar-label">{{ d.building }}</span>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: d.rate+'%', background: d.rate>=85?'#67c23a':d.rate>=80?'#e6a23c':'#f56c6c' }"></div>
              </div>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { getOverview } from '@/api/statistics'
import { useUserStore } from '@/store/user'
import StatCard from '@/components/stat-card/StatCard.vue'
import request from '@/api/request'

const userStore = useUserStore()
const roleLabel = computed(() => userStore.role === 'super_admin' ? '物业经理' : '城管监管')
const overview = ref({})
const bldData = ref([])
const trdData = ref([])
const trendChart = ref(null)
const loading = ref(true)

onMounted(async () => {
  try { const r = await getOverview(); overview.value = r.data } catch {}
  try {
    const [bR, tR] = await Promise.all([
      request.get('/admin/statistics/building-compare'),
      request.get('/admin/statistics/daily-trend'),
    ])
    bldData.value = bR.data
    trdData.value = tR.data
  } catch {}
  loading.value = false
  await nextTick()
  renderTrendChart()
})

function renderTrendChart() {
  if (!trendChart.value || !trdData.value.length) return
  const ec = window.echarts
  if (!ec) return
  const chart = ec.init(trendChart.value)
  const dates = trdData.value.map(d => d.date)
  const totals = trdData.value.map(d => d.total)
  const corrects = trdData.value.map(d => d.correct)
  const rates = trdData.value.map(d => d.rate)
  chart.setOption({
    tooltip: { trigger: 'axis', formatter: function(p) { return p[0].axisValue + '<br/>总投放: ' + p[0].value + '次<br/>正确: ' + p[1].value + '次<br/>正确率: ' + rates[p[0].dataIndex] + '%' } },
    legend: { data: ['总投放','正确','正确率'], top: 5 },
    grid: { top: 40, right: 60, bottom: 40, left: 50 },
    xAxis: { data: dates, axisLabel: { fontSize: 10, rotate: 45, interval: 2 } },
    yAxis: [
      { type: 'value', name: '次数', axisLabel: { fontSize: 10 } },
      { type: 'value', name: '%', min: 0, max: 100, axisLabel: { fontSize: 10, formatter: '{value}%' } }
    ],
    series: [
      { name: '总投放', type: 'bar', data: totals, itemStyle: { color: '#409eff', opacity: 0.6 }, barWidth: '40%' },
      { name: '正确', type: 'bar', data: corrects, itemStyle: { color: '#67c23a', opacity: 0.8 }, barWidth: '40%' },
      { name: '正确率', type: 'line', yAxisIndex: 1, data: rates, itemStyle: { color: '#f56c6c' }, lineStyle: { width: 2 }, symbol: 'circle', symbolSize: 5, markLine: { silent: true, data: [{ yAxis: 85, label: { formatter: '达标线 85%' }, lineStyle: { color: '#f56c6c', type: 'dashed' } }] } }
    ]
  })
}
</script>

<style scoped>
.dashboard { padding: 20px; }
.page-title { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 20px; }
.stat-row { margin-bottom: 16px; }
.bar-chart { padding: 10px 0; }
.bar-row { display: flex; align-items: center; margin-bottom: 6px; }
.bar-label { width: 36px; font-size: 12px; color: #606266; text-align: right; margin-right: 8px; flex-shrink: 0; }
.bar-track { flex: 1; height: 18px; background: #f0f2f5; border-radius: 4px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s; min-width: 2px; }
.bar-val { width: 44px; font-size: 12px; font-weight: 600; text-align: right; margin-left: 8px; flex-shrink: 0; }
</style>
