<template>
  <div class="detail-page">
    <div class="page-header">
      <h2>待处理设备</h2>
      <p class="subtitle">按社区查看离线/故障设备，每台设备在地图上单独标注</p>
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
          <el-table-column prop="deviceName" label="设备" width="160" />
          <el-table-column label="状态" width="70">
            <template #default="{ row }"><el-tag :type="row.status==='fault'?'danger':'warning'" size="small">{{ row.status==='fault'?'故障':'离线' }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="location" label="地址" min-width="200" />
          <el-table-column label="满溢度" width="80">
            <template #default="{ row }">{{ (row.fullRate*100).toFixed(0) }}%</template>
          </el-table-column>
          <el-table-column label="最后在线" width="140">
            <template #default="{ row }">{{ row.lastOnline?.slice(0,16) || '未知' }}</template>
          </el-table-column>
        </el-table>
        <div :id="'map-'+c.name" class="map-box"></div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
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
  await nextTick(); initMaps()
})

function initMaps() {
  setTimeout(() => {
    for (const c of groupedDevices.value) {
      const el = document.getElementById('map-'+c.name)
      if (!el || !window.L) continue
      // 找到所有有坐标的设备
      const valid = c.devices.filter(d => d.lat && d.lng)
      if (!valid.length) continue
      const center = [valid[0].lat, valid[0].lng]
      const map = window.L.map(el).setView(center, 16)
      window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OSM' }).addTo(map)
      for (const d of valid) {
        const color = d.status === 'fault' ? 'red' : 'orange'
        window.L.circleMarker([d.lat, d.lng], {
          radius: 8, fillColor: color, color: '#fff', weight: 2, fillOpacity: 0.8
        }).addTo(map).bindPopup('<b>'+d.deviceName+'</b><br>'+d.location+'<br>状态: '+(d.status==='fault'?'故障':'离线'))
      }
    }
  }, 600)
}
</script>

<style scoped>
.detail-page { padding: 24px; max-width: 900px; }
.page-header { margin-bottom: 20px; }
.page-header h2 { font-size: 20px; font-weight: 700; color: #303133; margin: 0 0 6px; }
.subtitle { font-size: 13px; color: #909399; margin: 0; }
.map-box { height: 220px; margin-top: 8px; border-radius: 8px; border: 1px solid #ebeef5; }
</style>
