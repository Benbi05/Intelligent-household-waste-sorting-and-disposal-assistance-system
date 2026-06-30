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
          <svg viewBox="0 0 600 220" class="trend-svg" v-loading="loading">
            <!-- 网格线 -->
            <line v-for="i in 4" :key="'h'+i" :x1="40" :y1="i*50" :x2="590" :y2="i*50" stroke="#f0f2f5" stroke-width="1"/>
            <!-- Y轴标签 -->
            <text v-for="i in 4" :key="'yt'+i" x="34" :y="i*50+4" text-anchor="end" font-size="10" fill="#c0c4cc">{{ 400-i*100 }}</text>
            <!-- 正确率折线 -->
            <polyline :points="ratePoints" fill="none" stroke="#f56c6c" stroke-width="2"/>
            <!-- 正确率圆点 -->
            <circle v-for="(p,i) in rateDots" :key="'rd'+i" :cx="p.x" :cy="p.y" r="3" fill="#f56c6c">
              <title>{{ trdData[i].date }} 正确率 {{ trdData[i].rate }}%</title>
            </circle>
            <!-- 总投放柱 -->
            <rect v-for="(d,i) in trdData" :key="'bar'+i" :x="42+i*18.3" :y="200-d.total*0.5" width="8" :height="d.total*0.5" fill="#409eff" opacity="0.6">
              <title>{{ d.date }} 总投放 {{ d.total }}次</title>
            </rect>
            <!-- 正确投放柱 -->
            <rect v-for="(d,i) in trdData" :key="'cbar'+i" :x="50+i*18.3" :y="200-d.correct*0.5" width="8" :height="d.correct*0.5" fill="#67c23a" opacity="0.8">
              <title>{{ d.date }} 正确 {{ d.correct }}次</title>
            </rect>
            <!-- X轴标签 -->
            <text v-for="(d,i) in xLabels" :key="'xl'+i" :x="46+i*18.3" y="216" font-size="9" fill="#c0c4cc" text-anchor="middle">{{ d }}</text>
            <!-- 图例 -->
            <rect x="440" y="5" width="12" height="12" fill="#409eff" opacity="0.6" rx="2"/>
            <text x="456" y="15" font-size="10" fill="#606266">总投放</text>
            <rect x="500" y="5" width="12" height="12" fill="#67c23a" opacity="0.8" rx="2"/>
            <text x="516" y="15" font-size="10" fill="#606266">正确</text>
            <circle cx="574" cy="11" r="4" fill="#f56c6c"/>
            <text x="582" y="15" font-size="10" fill="#606266">正确率</text>
          </svg>
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
const ratePoints = computed(() => trdData.value.map((d, i) => `${46+i*18.3},${200-d.rate*2}`).join(' '))
const rateDots = computed(() => trdData.value.map((d, i) => ({ x: 46+i*18.3, y: 200-d.rate*2 })))
const xLabels = computed(() => trdData.value.filter((_, i) => i % 3 === 0).map(d => d.date))
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

.trend-svg { width: 100%; height: auto; background: #fafbfc; border-radius: 6px; }
</style>
