<template>
  <div class="page">
    <div class="page-title">各社区用户统计</div>
    <el-table :data="list" v-loading="loading" border stripe empty-text="暂无数据" :default-sort="{ prop: 'totalUsers', order: 'descending' }">
      <el-table-column prop="community" label="社区" width="140" />
      <el-table-column prop="totalUsers" label="总用户数" sortable width="110" />
      <el-table-column prop="newUsers" label="本月新增" sortable width="100">
        <template #default="{ row }">
          <span :style="{ color: row.newUsers > 0 ? '#2e7d32' : '#78909c', fontWeight: '700' }">
            {{ row.newUsers > 0 ? '+' : '' }}{{ row.newUsers }}
          </span>
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
  try { const r = await request.get('/admin/community/user-stats'); list.value = r.data } catch {}
  loading.value = false
})
</script>

<style scoped>
.page { padding: 20px; }
.page-title { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 20px; }
</style>
