<template>
  <div class="detail-page">
    <div class="page-header">
      <h2>各社区用户统计</h2>
      <p class="subtitle">居民注册情况概览，点击列头按新增或总计排序</p>
    </div>
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6"><div class="sum-card"><div class="sum-val" style="color:#1a73e8">{{ totalUsers }}</div><div class="sum-label">总用户</div></div></el-col>
      <el-col :span="6"><div class="sum-card"><div class="sum-val" style="color:#2e7d32">{{ totalNew }}</div><div class="sum-label">本月新增</div></div></el-col>
    </el-row>
    <el-card shadow="never">
      <el-table :data="list" v-loading="loading" stripe size="medium" :default-sort="{ prop: 'totalUsers', order: 'descending' }">
        <el-table-column prop="community" label="社区" min-width="160" />
        <el-table-column prop="totalUsers" label="总用户数" sortable min-width="140">
          <template #default="{ row }">
            <div class="user-bar-wrap">
              <div class="user-bar"><div class="user-bar-fill" :style="{ width: maxU > 0 ? (row.totalUsers/maxU*100)+'%' : '0%' }"></div></div>
              <span class="user-num">{{ row.totalUsers }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="newUsers" label="本月新增" sortable min-width="140">
          <template #default="{ row }">
            <span :class="row.newUsers > 0 ? 'up' : 'flat'">
              {{ row.newUsers > 0 ? '+' : '' }}{{ row.newUsers }} 人
            </span>
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
const totalUsers = computed(() => list.value.reduce((s, d) => s + d.totalUsers, 0))
const totalNew = computed(() => list.value.reduce((s, d) => s + d.newUsers, 0))
const maxU = computed(() => Math.max(...list.value.map(d => d.totalUsers), 1))
onMounted(async () => {
  try { const r = await request.get('/admin/community/user-stats'); list.value = r.data } catch {}
  loading.value = false
})
</script>

<style scoped>
.detail-page { padding: 24px; max-width: none; }
.page-header { margin-bottom: 20px; }
.page-header h2 { font-size: 20px; font-weight: 700; color: #303133; margin: 0 0 6px; }
.subtitle { font-size: 13px; color: #909399; margin: 0; }
.stat-row { margin-bottom: 16px; }
.sum-card { text-align: center; padding: 16px; border-radius: 8px; background: #f5f7fa; }
.sum-val { font-size: 28px; font-weight: 700; }
.sum-label { font-size: 12px; color: #909399; margin-top: 4px; }
.user-bar-wrap { display: flex; align-items: center; gap: 10px; }
.user-bar { flex: 1; height: 8px; background: #f0f2f5; border-radius: 4px; overflow: hidden; }
.user-bar-fill { height: 100%; background: #1a73e8; border-radius: 4px; }
.user-num { font-weight: 700; font-size: 14px; min-width: 30px; }
.up { color: #2e7d32; font-weight: 600; }
.flat { color: #78909c; }
</style>
