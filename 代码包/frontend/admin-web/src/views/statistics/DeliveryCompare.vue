<template>
  <div class="detail-page">
    <div class="page-header">
      <h2>各社区投放总量对比</h2>
      <p class="subtitle">本月 vs 上月投放变化，按本月投放量降序排列</p>
    </div>
    <el-row :gutter="20" class="stat-row">
      <el-col :span="8" v-for="d in top3" :key="d.community">
        <div class="rank-card" :class="'rank-' + (top3.indexOf(d)+1)">
          <div class="rank-badge">{{ top3.indexOf(d)+1 }}</div>
          <div class="rank-info">
            <div class="rank-name">{{ d.community }}</div>
            <div class="rank-count">{{ d.thisMonth }}<small>次/月</small></div>
          </div>
        </div>
      </el-col>
    </el-row>
    <el-card shadow="never">
      <el-table :data="list" v-loading="loading" stripe size="medium" :default-sort="{ prop: 'thisMonth', order: 'descending' }">
        <el-table-column prop="community" label="社区" min-width="140" />
        <el-table-column prop="thisMonth" label="本月投放" sortable min-width="140">
          <template #default="{ row }"><span class="num">{{ row.thisMonth }}</span></template>
        </el-table-column>
        <el-table-column prop="lastMonth" label="上月投放" min-width="140">
          <template #default="{ row }"><span class="num sub">{{ row.lastMonth }}</span></template>
        </el-table-column>
        <el-table-column prop="change" label="环比变化" sortable min-width="140">
          <template #default="{ row }">
            <span :class="row.change > 0 ? 'up' : row.change < 0 ? 'down' : 'flat'">
              {{ row.change > 0 ? '+' : '' }}{{ row.change }} 次
            </span>
          </template>
        </el-table-column>
        <el-table-column label="趋势" min-width="200">
          <template #default="{ row }">
            <div class="spark-wrap">
              <div class="spark-bar">
                <div class="spark-this" :style="{ width: Math.max(row.thisMonth, row.lastMonth) > 0 ? (row.thisMonth / Math.max(row.thisMonth, row.lastMonth) * 100) + '%' : '0%' }"></div>
              </div>
              <div class="spark-bar">
                <div class="spark-last" :style="{ width: Math.max(row.thisMonth, row.lastMonth) > 0 ? (row.lastMonth / Math.max(row.thisMonth, row.lastMonth) * 100) + '%' : '0%' }"></div>
              </div>
              <span class="spark-label">{{ row.thisMonth >= row.lastMonth ? '↑' : '↓' }}</span>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import request from '@/api/request'
const list = ref([])
const loading = ref(true)
const top3 = computed(() => list.value.slice(0, 3))
onMounted(async () => {
  try { const r = await request.get('/admin/community/delivery-compare'); list.value = r.data } catch {}
  loading.value = false
})
</script>

<style scoped>
.detail-page { padding: 24px; max-width: none; }
.page-header { margin-bottom: 20px; }
.page-header h2 { font-size: 20px; font-weight: 700; color: #303133; margin: 0 0 6px; }
.subtitle { font-size: 13px; color: #909399; margin: 0; }
.stat-row { margin-bottom: 16px; }
.rank-card { display: flex; align-items: center; padding: 16px; border-radius: 10px; background: #fff; border: 1px solid #ebeef5; gap: 14px; }
.rank-card.rank-1 { border-left: 4px solid #ff9800; background: #fff8e1; }
.rank-card.rank-2 { border-left: 4px solid #90a4ae; background: #f5f7fa; }
.rank-card.rank-3 { border-left: 4px solid #a1887f; background: #fafafa; }
.rank-badge { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 800; color: #fff; flex-shrink: 0; }
.rank-1 .rank-badge { background: linear-gradient(135deg, #ff9800, #f57c00); }
.rank-2 .rank-badge { background: linear-gradient(135deg, #90a4ae, #78909c); }
.rank-3 .rank-badge { background: linear-gradient(135deg, #8d6e63, #6d4c41); }
.rank-name { font-size: 15px; font-weight: 600; color: #303133; }
.rank-count { font-size: 22px; font-weight: 700; color: #1a73e8; }
.rank-count small { font-size: 12px; font-weight: 400; color: #909399; margin-left: 2px; }
.num { font-weight: 700; font-size: 15px; color: #303133; }
.num.sub { color: #909399; }
.up { color: #2e7d32; font-weight: 600; }
.down { color: #c62828; font-weight: 600; }
.flat { color: #78909c; }
.spark-wrap { display: flex; align-items: center; gap: 6px; }
.spark-bar { width: 40px; height: 6px; background: #f0f2f5; border-radius: 3px; overflow: hidden; }
.spark-this { height: 100%; background: #1a73e8; border-radius: 3px; }
.spark-last { height: 100%; background: #c0c4cc; border-radius: 3px; }
.spark-label { font-size: 14px; }
</style>
