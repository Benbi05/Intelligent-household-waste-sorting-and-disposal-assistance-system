<template>
  <div class="detail-page">
    <div class="page-header">
      <h2>各社区分类正确率</h2>
      <p class="subtitle">按品类筛选查看，正确率低于 85% 需整改</p>
    </div>
    <div class="filter-bar">
      <el-radio-group v-model="catFilter" @change="fetchData" size="default">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="recyclable">♻ 可回收物</el-radio-button>
        <el-radio-button value="kitchen">🍲 厨余垃圾</el-radio-button>
        <el-radio-button value="hazardous">☣ 有害垃圾</el-radio-button>
        <el-radio-button value="other">🗑 其他垃圾</el-radio-button>
      </el-radio-group>
    </div>
    <el-card shadow="never">
      <el-table :data="list" v-loading="loading" stripe size="medium" :default-sort="{ prop: 'rate', order: 'descending' }">
        <el-table-column prop="community" label="社区" min-width="160" />
        <el-table-column prop="rate" label="正确率" sortable min-width="160">
          <template #default="{ row }">
            <div class="rate-cell">
              <div class="rate-bar-bg"><div class="rate-bar" :style="{ width: row.rate+'%', background: row.rate>=85?'#2e7d32':row.rate>=75?'#ef6c00':'#c62828' }"></div></div>
              <span :class="row.rate>=85?'rate-ok':row.rate>=75?'rate-warn':'rate-bad'">{{ row.rate }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="correct" label="正确" sortable min-width="100" />
        <el-table-column prop="total" label="总量" sortable min-width="100" />
        <el-table-column label="达标" min-width="100">
          <template #default="{ row }">
            <el-tag :type="row.rate>=85?'success':row.rate>=75?'warning':'danger'" size="small" effect="dark">
              {{ row.rate>=85?'达标':row.rate>=75?'接近':'未达标' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/api/request'
const list = ref([])
const catFilter = ref('')
const loading = ref(true)
async function fetchData() {
  loading.value = true
  try {
    const r = await request.get('/admin/community/rate-compare', { params: { categoryType: catFilter.value } })
    list.value = r.data.sort((a, b) => b.rate - a.rate)
  } catch {}
  loading.value = false
}
onMounted(fetchData)
</script>

<style scoped>
.detail-page { padding: 24px; max-width: none; }
.page-header { margin-bottom: 20px; }
.page-header h2 { font-size: 20px; font-weight: 700; color: #303133; margin: 0 0 6px; }
.subtitle { font-size: 13px; color: #909399; margin: 0; }
.filter-bar { margin-bottom: 16px; }
.rate-cell { display: flex; align-items: center; gap: 10px; }
.rate-bar-bg { width: 100px; height: 8px; background: #f0f2f5; border-radius: 4px; overflow: hidden; }
.rate-bar { height: 100%; border-radius: 4px; transition: width .3s; }
.rate-ok { font-weight: 700; color: #2e7d32; font-size: 15px; }
.rate-warn { font-weight: 700; color: #ef6c00; font-size: 15px; }
.rate-bad { font-weight: 700; color: #c62828; font-size: 15px; }
</style>
