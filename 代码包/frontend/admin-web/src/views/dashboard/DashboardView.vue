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
            <div class="bar-legend"><span class="dot red"></span> 红线 = 城管考核达标线 85%</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="24">
        <el-card shadow="never">
          <template #header>近30天投放趋势 <span style="font-size:12px;color:#c0c4cc;font-weight:normal">— 蓝=总投放 绿=正确</span></template>
          <div class="trend-chart" v-loading="loading">
            <div class="trend-legend">
              <span><span class="l-dot" style="background:#409eff"></span> 总投放</span>
              <span><span class="l-dot" style="background:#67c23a"></span> 正确</span>
              <span><span class="l-dot" style="background:#f56c6c;border-radius:50%;width:8px;height:8px"></span> 正确率</span>
            </div>
            <div class="trend-bars">
              <div v-for="(d,i) in trdData" :key="i" class="t-day">
                <div class="t-bar-wrap">
                  <div class="t-bar t-total" :style="{height:(d.total*0.45)+'px'}" :title="d.date+' 总投放 '+d.total+'次'"></div>
                  <div class="t-bar t-correct" :style="{height:(d.correct*0.45)+'px'}" :title="d.date+' 正确 '+d.correct+'次'"></div>
                  <div class="t-dot" :style="{bottom:(d.rate*1.8)+'px'}" :title="d.date+' 正确率 '+d.rate+'%'"></div>
                </div>
                <span class="t-date" v-if="i%3===0" :title="d.date">{{ d.date.slice(3) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getOverview } from '@/api/statistics'
import { useUserStore } from '@/store/user'
import StatCard from '@/components/stat-card/StatCard.vue'
import request from '@/api/request'

const userStore = useUserStore()
const roleLabel = computed(() => userStore.role === 'super_admin' ? '物业经理' : '城管监管')
const overview = ref({})
const bldData = ref([])
const trdData = ref([])
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
})
</script>

<style scoped>
.dashboard { padding: 20px; }
.page-title { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 20px; }
.stat-row { margin-bottom: 16px; }

.bar-chart { padding: 10px 0; }
.bar-row { display: flex; align-items: center; margin-bottom: 6px; }
.bar-label { width: 36px; font-size: 12px; color: #606266; text-align: right; margin-right: 8px; flex-shrink: 0; }
.bar-track { flex: 1; height: 18px; background: #f0f2f5; border-radius: 4px; overflow: hidden; position: relative; }
.bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s; min-width: 2px; }
.bar-val { width: 44px; font-size: 12px; font-weight: 600; text-align: right; margin-left: 8px; flex-shrink: 0; }
.bar-legend { margin-top: 12px; font-size: 11px; color: #c0c4cc; }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
.dot.red { background: #f56c6c; }

.trend-chart { background: #fafbfc; border-radius: 6px; padding: 8px 0; }
.trend-legend { display: flex; gap: 20px; justify-content: center; margin-bottom: 10px; font-size: 12px; color: #606266; }
.l-dot { display: inline-block; width: 10px; height: 10px; border-radius: 2px; vertical-align: middle; margin-right: 2px; }
.trend-bars { display: flex; align-items: flex-end; height: 200px; padding: 0 8px; gap: 2px; }
.t-day { flex: 1; display: flex; flex-direction: column; align-items: center; min-width: 0; }
.t-bar-wrap { width: 100%; height: 180px; position: relative; display: flex; align-items: flex-end; justify-content: center; gap: 1px; }
.t-bar { width: 4px; border-radius: 2px 2px 0 0; min-height: 2px; }
.t-total { background: #409eff; opacity: 0.5; }
.t-correct { background: #67c23a; opacity: 0.8; }
.t-dot { position: absolute; width: 4px; height: 4px; background: #f56c6c; border-radius: 50%; left: 50%; transform: translateX(-50%); }
.t-date { font-size: 9px; color: #c0c4cc; margin-top: 4px; white-space: nowrap; }
</style>
