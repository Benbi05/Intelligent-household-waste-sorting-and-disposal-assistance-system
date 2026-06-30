<template>
  <div class="page">
    <div class="page-title">各社区投放总量对比</div>
    <el-table :data="list" v-loading="loading" border stripe empty-text="暂无数据" :default-sort="{ prop: 'thisMonth', order: 'descending' }">
      <el-table-column prop="community" label="社区" width="140" />
      <el-table-column prop="thisMonth" label="本月投放" sortable width="110" />
      <el-table-column prop="lastMonth" label="上月投放" sortable width="110" />
      <el-table-column prop="change" label="环比变化" sortable width="100">
        <template #default="{ row }">
          <span :style="{ color: row.change > 0 ? '#2e7d32' : row.change < 0 ? '#c62828' : '#78909c', fontWeight: '700' }">
            {{ row.change > 0 ? '+' : '' }}{{ row.change }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="rate" label="变化趋势" width="100">
        <template #default="{ row }">
          <span v-if="row.change > 0" style="color:#2e7d32">↑ 增长</span>
          <span v-else-if="row.change < 0" style="color:#c62828">↓ 下降</span>
          <span v-else style="color:#78909c">— 持平</span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/api/request'
const list = ref([])
const loading = ref(true)
onMounted(async () => {
  try { const r = await request.get('/admin/community/delivery-compare'); list.value = r.data } catch {}
  loading.value = false
})
</script>

<style scoped>
.page { padding: 20px; }
.page-title { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 20px; }
</style>
