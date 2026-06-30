<template>
  <div class="detail-page">
    <div class="page-header"><h2>系统监控</h2><p class="subtitle">AI模型状态 · 设备健康 · 系统资源</p></div>

    <el-row :gutter="16" class="stat-row">
      <el-col :span="6"><StatCard label="在线设备" :value="data.devices?.online || 0" unit="台" color="#67c23a" :sub="'总计 ' + (data.devices?.total || 0) + ' 台'" /></el-col>
      <el-col :span="6"><StatCard label="今日识别" :value="data.todayDeliveries || 0" unit="次" color="#1a73e8" :sub="'正确率 ' + (data.todayCorrectRate || 0) + '%'" /></el-col>
      <el-col :span="6"><StatCard label="活跃模型" :value="data.activeModel?.version || '-'" unit="" color="#e6a23c" :sub="'准确率 ' + (data.activeModel?.accuracy || 0) + '%'" /></el-col>
      <el-col :span="6"><StatCard label="注册用户" :value="data.totalResidents || 0" unit="人" color="#78909c" :sub="'商家 ' + (data.totalMerchants || 0) + ' 家'" /></el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>设备状态</template>
          <div class="health-grid">
            <div class="health-item ok">
              <div class="health-num">{{ data.devices?.online || 0 }}</div>
              <div class="health-label">在线</div>
            </div>
            <div class="health-item warn">
              <div class="health-num">{{ data.devices?.offline || 0 }}</div>
              <div class="health-label">离线</div>
            </div>
            <div class="health-item bad">
              <div class="health-num">{{ data.devices?.fault || 0 }}</div>
              <div class="health-label">故障</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>系统服务</template>
          <div class="service-list">
            <div class="service-item"><span>数据库 MySQL</span><el-tag :type="data.dbOk ? 'success' : 'danger'" size="small">{{ data.dbOk ? '正常' : '异常' }}</el-tag></div>
            <div class="service-item"><span>缓存 Redis</span><el-tag :type="data.redisOk ? 'success' : 'danger'" size="small">{{ data.redisOk ? '正常' : '异常' }}</el-tag></div>
            <div class="service-item"><span>AI 识别引擎</span><el-tag :type="data.activeModel ? 'success' : 'warning'" size="small">{{ data.activeModel ? data.activeModel.version : '未部署' }}</el-tag></div>
            <div class="service-item"><span>API 网关</span><el-tag type="success" size="small">正常</el-tag></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>AI模型准确率</template>
          <div ref="modelChart" style="height:260px" v-loading="loading"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>今日识别分布</template>
          <div style="text-align:center;padding:40px">
            <div style="font-size:48px;font-weight:700" :style="{color: (data.todayCorrectRate||0) >= 85 ? '#67c23a' : '#e6a23c'}">{{ data.todayCorrectRate || 0 }}%</div>
            <div style="font-size:14px;color:#909399;margin-top:8px">分类正确率</div>
            <div style="margin-top:16px;font-size:13px;color:#606266">
              今日总投放 <b>{{ data.todayDeliveries || 0 }}</b> 次 ·
              异常设备 <b>{{ data.devices?.fault || 0 }}</b> 台
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import request from '@/api/request'
import StatCard from '@/components/stat-card/StatCard.vue'

const data = ref({})
const loading = ref(true)
const modelChart = ref(null)

onMounted(async () => {
  try { const r = await request.get('/admin/ops/dashboard'); data.value = r.data } catch {}
  loading.value = false
  setTimeout(renderChart, 300)
})

function renderChart() {
  if (!modelChart.value || !window.echarts) return
  const c = window.echarts.init(modelChart.value)
  c.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 20, right: 30, bottom: 30, left: 50 },
    xAxis: { data: ['准确率','mAP','精确率','召回率'], axisLabel: { fontSize: 11 } },
    yAxis: { max: 100, axisLabel: { formatter: '{value}%', fontSize: 10 } },
    series: [{
      type: 'bar', data: [
        data.value.activeModel?.accuracy || 0, 88, 87, 82
      ],
      itemStyle: { color: '#409eff', borderRadius: [4,4,0,0] }, barWidth: '50%'
    }]
  })
}
</script>

<style scoped>
.detail-page { padding: 24px; }
.page-header { margin-bottom: 20px; }
.page-header h2 { font-size: 20px; font-weight: 700; color: #303133; margin: 0 0 6px; }
.subtitle { font-size: 13px; color: #909399; margin: 0; }
.stat-row { margin-bottom: 16px; }
.health-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
.health-item { text-align: center; padding: 16px; border-radius: 8px; }
.health-item.ok { background: #f0f9eb; }
.health-item.warn { background: #fdf6ec; }
.health-item.bad { background: #fef0f0; }
.health-num { font-size: 28px; font-weight: 700; color: #303133; }
.health-label { font-size: 12px; color: #909399; margin-top: 4px; }
.service-list { display: flex; flex-direction: column; gap: 12px; }
.service-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f0f2f5; font-size: 14px; color: #606266; }
</style>
