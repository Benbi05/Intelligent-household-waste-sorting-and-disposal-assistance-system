<template>
  <div class="page">
    <div class="page-title">各社区分类正确率</div>
    <div style="margin-bottom:12px">
      <el-radio-group v-model="catFilter" @change="fetchData" size="small">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="recyclable">可回收物</el-radio-button>
        <el-radio-button value="kitchen">厨余垃圾</el-radio-button>
        <el-radio-button value="hazardous">有害垃圾</el-radio-button>
        <el-radio-button value="other">其他垃圾</el-radio-button>
      </el-radio-group>
    </div>
    <el-table :data="list" v-loading="loading" border stripe empty-text="暂无数据" :default-sort="{ prop: 'rate', order: 'descending' }">
      <el-table-column prop="community" label="社区" width="140" />
      <el-table-column prop="rate" label="正确率" sortable width="110">
        <template #default="{ row }">
          <span :style="{ color: row.rate >= 85 ? '#2e7d32' : row.rate >= 75 ? '#ef6c00' : '#c62828', fontWeight: '700' }">{{ row.rate }}%</span>
        </template>
      </el-table-column>
      <el-table-column prop="correct" label="正确" sortable width="90" />
      <el-table-column prop="total" label="总计" sortable width="90" />
    </el-table>
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
.page { padding: 20px; }
.page-title { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 20px; }
</style>
