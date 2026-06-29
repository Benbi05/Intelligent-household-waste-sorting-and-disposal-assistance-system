<template>
  <div class="page-container">
    <h2 class="page-title">数据统计</h2>

    <!-- 概览卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="12" :lg="8" v-for="card in statCards" :key="card.label">
        <StatCard :label="card.label" :value="card.value" :color="card.color" :trend="card.trend">
          <template #icon><el-icon :size="24"><component :is="card.icon" /></el-icon></template>
        </StatCard>
      </el-col>
    </el-row>

    <!-- 投放趋势 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="24">
        <div class="page-card">
          <div class="card-header">
            <h3 class="card-title">投放数据统计</h3>
            <div class="card-filters">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DDTHH:mm:ss"
                style="width:260px"
                @change="fetchDelivery"
              />
              <el-input v-model="deliveryForm.area" placeholder="区域筛选" clearable style="width:140px;margin-left:10px" @keyup.enter="fetchDelivery" @clear="fetchDelivery" />
              <el-button type="primary" style="margin-left:10px" @click="handleExport">
                <el-icon><Download /></el-icon>导出数据
              </el-button>
            </div>
          </div>

          <el-row :gutter="20" class="delivery-stats">
            <el-col :span="6">
              <div class="mini-stat">
                <div class="mini-value">{{ deliveryStats.totalDeliveryCount }}</div>
                <div class="mini-label">总投递次数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="mini-stat">
                <div class="mini-value">{{ deliveryStats.correctCount }}</div>
                <div class="mini-label">正确投递</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="mini-stat">
                <div class="mini-value">{{ deliveryStats.incorrectCount }}</div>
                <div class="mini-label">错误投递</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="mini-stat">
                <div class="mini-value">{{ (deliveryStats.correctRate * 100).toFixed(1) }}%</div>
                <div class="mini-label">正确率</div>
              </div>
            </el-col>
          </el-row>

          <!-- 简单柱状图示意 -->
          <div class="chart-placeholder" v-if="deliveryStats.totalDeliveryCount > 0">
            <div class="bar-chart">
              <div class="bar-col">
                <div class="bar correct" :style="{ height: correctPercent + '%' }"></div>
                <span class="bar-label">正确 ({{ correctPercent }}%)</span>
              </div>
              <div class="bar-col">
                <div class="bar incorrect" :style="{ height: incorrectPercent + '%' }"></div>
                <span class="bar-label">错误 ({{ incorrectPercent }}%)</span>
              </div>
            </div>
            <div class="points-info">
              总发放积分：<strong>{{ deliveryStats.totalPointsAwarded }}</strong>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { User, Monitor, Delete, Coin, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getOverview, getDeliveryStats, exportData } from '@/api/statistics'
import StatCard from '@/components/stat-card/StatCard.vue'

const overview = reactive({
  totalUsers: 0, onlineDevices: 0, totalDevices: 0,
  todayDeliveryCount: 0, monthCorrectRate: 0, pendingMerchantCount: 0,
})

const deliveryStats = reactive({
  totalDeliveryCount: 0, correctCount: 0, incorrectCount: 0,
  correctRate: 0, totalPointsAwarded: 0,
})

const dateRange = ref([])
const deliveryForm = reactive({ area: '' })

const statCards = computed(() => [
  { label: '用户总数', value: overview.totalUsers, color: '#67c23a', trend: 0, icon: User },
  { label: '在线设备 / 总设备', value: `${overview.onlineDevices} / ${overview.totalDevices}`, color: '#409eff', trend: 0, icon: Monitor },
  { label: '今日投递次数', value: overview.todayDeliveryCount, color: '#e6a23c', trend: 0, icon: Delete },
  { label: '待审核商家', value: overview.pendingMerchantCount, color: '#f56c6c', trend: 0, icon: Coin },
])

const correctPercent = computed(() => {
  if (deliveryStats.totalDeliveryCount === 0) return 0
  return Math.round((deliveryStats.correctCount / deliveryStats.totalDeliveryCount) * 100)
})
const incorrectPercent = computed(() => 100 - correctPercent.value)

async function fetchOverview() {
  try {
    const res = await getOverview()
    Object.assign(overview, res.data)
  } catch { /* handled */ }
}

async function fetchDelivery() {
  try {
    const params = { area: deliveryForm.area }
    if (dateRange.value && dateRange.value.length === 2) {
      params.startTime = dateRange.value[0]
      params.endTime = dateRange.value[1]
    }
    const res = await getDeliveryStats(params)
    Object.assign(deliveryStats, res.data)
  } catch { /* handled */ }
}

async function handleExport() {
  try {
    const res = await exportData()
    ElMessage.success('导出任务已创建：' + res.data.exportUrl)
  } catch { /* handled */ }
}

onMounted(() => { fetchOverview(); fetchDelivery() })
</script>

<style scoped>
.stat-row { margin-bottom: 20px; }
.chart-row { margin-top: 0; }
.card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }
.card-title { font-size: 16px; font-weight: 600; color: #1a1a1a; margin: 0; }
.card-filters { display: flex; align-items: center; }
.delivery-stats { padding: 8px 0 20px; }
.mini-stat { text-align: center; padding: 12px; background: #f5f7fa; border-radius: 8px; }
.mini-value { font-size: 24px; font-weight: 700; color: #1a1a1a; }
.mini-label { font-size: 13px; color: #909399; margin-top: 4px; }
.chart-placeholder { text-align: center; padding-top: 8px; }
.bar-chart { display: flex; justify-content: center; gap: 60px; align-items: flex-end; height: 160px; }
.bar-col { display: flex; flex-direction: column; align-items: center; width: 80px; height: 100%; justify-content: flex-end; }
.bar { width: 40px; border-radius: 6px 6px 0 0; min-height: 4px; transition: height 0.5s; }
.bar.correct { background: linear-gradient(to top, #67c23a, #85ce61); }
.bar.incorrect { background: linear-gradient(to top, #f56c6c, #f89898); }
.bar-label { font-size: 12px; color: #909399; margin-top: 8px; }
.points-info { margin-top: 12px; font-size: 14px; color: #606266; }
</style>
