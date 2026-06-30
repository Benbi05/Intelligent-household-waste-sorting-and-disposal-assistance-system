<template>
  <div class="dashboard">
    <div class="page-title">{{ roleLabel }}工作台 — 虎溪花园社区（沙坪坝区虎溪街道）</div>
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6"><StatCard label="本月投放总量" :value="overview.monthDeliveryCount || 0" unit="次" color="#409eff" tip="全社区30天垃圾投放总次数" /></el-col>
      <el-col :span="6"><StatCard label="分类正确率" :value="overview.monthCorrectRate ? (overview.monthCorrectRate*100).toFixed(1) : 0" unit="%" color="#67c23a" tip="正确投放占比，达标线85%" /></el-col>
      <el-col :span="6"><StatCard label="在线设备" :value="overview.onlineDevices || 0" :unit="'/' + (overview.totalDevices || 0) + '台'" color="#e6a23c" tip="正常运行垃圾箱 / 总数" /></el-col>
      <el-col :span="6"><StatCard label="注册用户" :value="overview.totalUsers || 0" unit="人" color="#f56c6c" tip="已注册小程序居民数量" /></el-col>
    </el-row>
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>各栋分类正确率对比 <span style="font-size:12px;color:#c0c4cc;font-weight:normal">— 红线=考核达标线85%，绿柱达标红柱未达标</span></template>
          <div ref="bldChart" style="height:300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>近30天投放趋势 <span style="font-size:12px;color:#c0c4cc;font-weight:normal">— 蓝=投放总量，绿=正确投放</span></template>
          <div ref="trendChart" style="height:300px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getOverview } from '@/api/statistics'
import { useUserStore } from '@/store/user'
import StatCard from '@/components/stat-card/StatCard.vue'
import request from '@/api/request'

const userStore = useUserStore()
const roleLabel = computed(() => userStore.role === 'super_admin' ? '物业经理' : '城管监管')
const overview = ref({})
const bldChart = ref(null)
const trendChart = ref(null)

onMounted(async () => {
  try { const r = await getOverview(); overview.value = r.data } catch {}
  setTimeout(loadCharts, 300)
})

async function loadCharts() {
  try {
    const [bR, tR] = await Promise.all([request.get('/admin/statistics/building-compare'), request.get('/admin/statistics/daily-trend')])
    const bld = bR.data; const trd = tR.data
    if (bldChart.value) {
      const c = echarts.init(bldChart.value)
      c.setOption({
        tooltip: { trigger: 'axis', formatter: function(p) { const d = p[0]; return d.name + '<br/>正确率: ' + d.value + '%<br/>' + (d.value>=85?'✅ 达标':d.value>=80?'⚠️ 接近达标':'❌ 未达标') } },
        xAxis: { data: bld.map(d => d.building), axisLabel: { fontSize: 11 } },
        yAxis: { max: 100, axisLabel: { formatter: '{value}%' } },
        series: [{ name: '正确率', type: 'bar', data: bld.map(d => d.rate),
          itemStyle: { color: p => p.value>=85?'#67c23a':p.value>=80?'#e6a23c':'#f56c6c' },
          markLine: { data: [{ yAxis: 85, name: '达标线 85%', lineStyle: { color: '#f56c6c', type: 'dashed', width: 2 } }], label: { show: true, fontSize: 11 } } }],
        grid: { top: 20, right: 30, bottom: 30, left: 40 }
      })
    }
    if (trendChart.value) {
      const c = echarts.init(trendChart.value)
      c.setOption({
        tooltip: { trigger: 'axis', formatter: function(p) { return p[0].axisValue + '<br/>总投放: ' + p[0].value + '次<br/>正确: ' + p[1].value + '次<br/>正确率: ' + (p[1].value/p[0].value*100).toFixed(1) + '%' } },
        xAxis: { data: trd.map(d => d.date), axisLabel: { fontSize: 10, rotate: 45 } },
        series: [{ name: '总投放', type: 'bar', data: trd.map(d => d.total), itemStyle: { color: '#409eff' } },
                 { name: '正确', type: 'bar', data: trd.map(d => d.correct), itemStyle: { color: '#67c23a' } }],
        legend: { data: ['总投放','正确'] },
        grid: { top: 40, right: 20, bottom: 40, left: 50 }
      })
    }
  } catch {}
}
</script>

<style scoped>
.dashboard { padding: 20px; }
.page-title { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 20px; }
.stat-row { margin-bottom: 16px; }
</style>
