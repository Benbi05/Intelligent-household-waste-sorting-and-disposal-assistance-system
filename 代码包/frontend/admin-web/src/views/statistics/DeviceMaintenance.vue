<template>
  <div class="page">
    <div class="page-title">待处理设备 — 按社区查看</div>

    <el-collapse v-model="activeCommunities" v-loading="loading">
      <el-collapse-item v-for="c in groupedDevices" :key="c.name" :title="`${c.name}（${c.devices.length}台待处理）`" :name="c.name">
        <el-table :data="c.devices" size="small" border stripe>
          <el-table-column prop="deviceName" label="设备名称" width="160" />
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 'fault' ? 'danger' : 'warning'" size="small">{{ row.status === 'fault' ? '故障' : '离线' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="location" label="地址" min-width="200" />
          <el-table-column label="满溢度" width="80">
            <template #default="{ row }">{{ (row.fullRate * 100).toFixed(0) }}%</template>
          </el-table-column>
          <el-table-column label="最后在线" width="160">
            <template #default="{ row }">{{ row.lastOnline?.slice(0,16) || '未知' }}</template>
          </el-table-column>
        </el-table>
        <!-- 地图 -->
        <div :id="'map-' + c.name" style="height:200px;margin-top:8px;border-radius:6px"></div>
      </el-collapse-item>
    </el-collapse>
    <div v-if="!loading && groupedDevices.length === 0" style="text-align:center;color:#c0c4cc;padding:40px">所有设备运行正常 ✅</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import request from '@/api/request'

const list = ref([])
const loading = ref(true)
const activeCommunities = ref([])

const groupedDevices = computed(() => {
  const map = {}
  for (const d of list.value) {
    if (!map[d.community]) map[d.community] = []
    map[d.community].push(d)
  }
  return Object.entries(map).map(([name, devices]) => ({ name, devices }))
})

onMounted(async () => {
  try { const r = await request.get('/admin/community/device-issues'); list.value = r.data } catch {}
  loading.value = false
  await nextTick()
  initMaps()
})

function initMaps() {
  // 虎溪街道各社区大致坐标
  const positions = {
    '虎溪花园': [29.6098, 106.2996],
    '学府悦园': [29.6112, 106.3051],
    '康居西城': [29.6055, 106.2930],
    '龙湖U城': [29.6130, 106.3085],
    '金科廊桥水乡': [29.6032, 106.2880],
    '富力城': [29.6070, 106.3020],
    '恒大未来城': [29.6150, 106.3120],
    '融创文旅城': [29.6190, 106.2950],
  }
  setTimeout(() => {
    for (const c of groupedDevices.value) {
      const el = document.getElementById('map-' + c.name)
      if (!el || !window.L) continue
      const pos = positions[c.name] || [29.6098, 106.2996]
      const map = window.L.map(el).setView(pos, 15)
      window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OSM'
      }).addTo(map)
      window.L.marker(pos).addTo(map).bindPopup(c.name + ' - ' + c.devices.length + '台待处理')
    }
  }, 500)
}
</script>

<style scoped>
.page { padding: 20px; }
.page-title { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 20px; }
</style>
