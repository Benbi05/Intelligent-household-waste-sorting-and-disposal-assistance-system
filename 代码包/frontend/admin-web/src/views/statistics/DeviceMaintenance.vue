<template>
  <div class="detail-page">
    <div class="page-header">
      <h2>待处理设备</h2>
      <p class="subtitle">按社区查看离线/故障设备详情</p>
    </div>
    <el-empty v-if="!loading && allDevices.length === 0" description="所有设备运行正常" />
    <el-collapse v-model="activeComms" v-loading="loading" v-else>
      <el-collapse-item v-for="c in groupedDevices" :key="c.name" :name="c.name">
        <template #title>
          <div style="display:flex;align-items:center;gap:8px">
            <el-tag :type="c.devices.some(d=>d.status==='fault')?'danger':'warning'" size="small">{{ c.devices.length }}台</el-tag>
            <span style="font-weight:600">{{ c.name }}</span>
          </div>
        </template>
        <el-table :data="c.devices" size="small" border stripe>
          <el-table-column prop="deviceName" label="设备名称" width="180" />
          <el-table-column label="状态" min-width="100">
            <template #default="{ row }"><el-tag :type="row.status==='fault'?'danger':'warning'" size="small">{{ row.status==='fault'?'故障':'离线' }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="location" label="安装位置" min-width="220" />
          <el-table-column label="满溢度" min-width="100">
            <template #default="{ row }">
              <div class="full-bar"><div class="full-bar-fill" :style="{ width: (row.fullRate*100)+'%', background: row.fullRate>0.8?'#c62828':row.fullRate>0.5?'#ef6c00':'#2e7d32' }"></div></div>
              <span style="font-size:12px">{{ (row.fullRate*100).toFixed(0) }}%</span>
            </template>
          </el-table-column>
          <el-table-column label="最后在线" width="160">
            <template #default="{ row }">{{ row.lastOnline?.slice(0,16) || '未知' }}</template>
          </el-table-column>
        </el-table>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import request from '@/api/request'

const allDevices = ref([])
const loading = ref(true)
const activeComms = ref([])

const groupedDevices = computed(() => {
  const map = {}
  for (const d of allDevices.value) {
    if (!map[d.community]) map[d.community] = []
    map[d.community].push(d)
  }
  return Object.entries(map).map(([name, devices]) => ({ name, devices }))
})

onMounted(async () => {
  try { const r = await request.get('/admin/community/device-issues'); allDevices.value = r.data } catch {}
  loading.value = false
})
</script>

<style scoped>
.detail-page { padding: 24px; max-width: none; }
.page-header { margin-bottom: 20px; }
.page-header h2 { font-size: 20px; font-weight: 700; color: #303133; margin: 0 0 6px; }
.subtitle { font-size: 13px; color: #909399; margin: 0; }
.full-bar { display: inline-block; width: 60px; height: 8px; background: #f0f2f5; border-radius: 4px; overflow: hidden; vertical-align: middle; margin-right: 6px; }
.full-bar-fill { height: 100%; border-radius: 4px; }
</style>
