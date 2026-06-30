<template>
  <div class="page">
    <div class="page-title">虎溪街道 8 个社区对比</div>
    <el-table :data="list" v-loading="loading" border stripe size="small" empty-text="暂无数据">
      <el-table-column prop="name" label="社区" width="140" />
      <el-table-column prop="total" label="本月投放" sortable width="100" />
      <el-table-column prop="correctRate" label="分类正确率" sortable width="120">
        <template #default="{ row }">
          <span :style="{ color: row.correctRate>=85?'#67c23a':row.correctRate>=80?'#e6a23c':'#f56c6c', fontWeight:'700' }">{{ row.correctRate }}%</span>
          <el-tag v-if="row.correctRate>=85" size="small" type="success">达标</el-tag>
          <el-tag v-else-if="row.correctRate>=80" size="small" type="warning">接近</el-tag>
          <el-tag v-else size="small" type="danger">未达标</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="onlineDevices" label="在线设备" width="100" />
      <el-table-column prop="totalDevices" label="总设备" width="100" />
      <el-table-column prop="users" label="注册用户" width="100" />
      <el-table-column prop="points" label="积分发放" width="110" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <span v-if="row.correctRate>=85" style="color:#67c23a">✅ 及格</span>
          <span v-else style="color:#f56c6c">❌ 需整改</span>
        </template>
      </el-table-column>
    </el-table>
    <div style="margin-top:12px;font-size:12px;color:#c0c4cc">
      达标线 85% | 接近达标 80-85% | 未达标 &lt;80% — 未达标社区将收到整改通知
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/api/request'

const list = ref([])
const loading = ref(true)

const communities = [
  { name: '虎溪花园', prefix: '虎溪' },
  { name: '学府悦园', prefix: '学府' },
  { name: '康居西城', prefix: '康居' },
  { name: '龙湖U城', prefix: '龙湖' },
  { name: '金科廊桥水乡', prefix: '金科' },
  { name: '富力城', prefix: '富力' },
  { name: '恒大未来城', prefix: '恒大' },
  { name: '融创文旅城', prefix: '融创' },
]

onMounted(async () => {
  try {
    const res = await request.get('/admin/statistics/building-compare')
    const data = res.data
    // 按社区前缀聚合
    const map = {}
    for (const d of data) {
      const prefix = d.building.includes('栋') ? '虎溪' : d.deviceId?.slice(0,2) || '未知'
      // 从 device 前缀聚合
    }
    // 为每个社区单独查询概览
    const results = []
    for (const c of communities) {
      try {
        const r = await request.get('/admin/statistics/overview', { params: { community: c.prefix } })
        const o = r.data
        const bld = await request.get('/admin/statistics/building-compare')
        const bldData = (bld.data || []).filter(d => d.building && d.building.includes(c.prefix))
        const total = bldData.reduce((s, d) => s + d.total, 0)
        const correct = bldData.reduce((s, d) => s + d.correct, 0)
        const rate = total ? (correct/total*100).toFixed(1) : '0.0'
        results.push({
          name: c.name,
          total,
          correctRate: Number(rate),
          onlineDevices: o.onlineDevices || 0,
          totalDevices: o.totalDevices || 0,
          users: o.totalUsers || 0,
          points: bldData.reduce((s, d) => s + (d.points||0), 0),
        })
      } catch { results.push({ name: c.name, total: 0, correctRate: 0, onlineDevices: 0, totalDevices: 0, users: 0, points: 0 }) }
    }
    list.value = results.sort((a, b) => b.correctRate - a.correctRate)
  } catch {}
  loading.value = false
})
</script>

<style scoped>
.page { padding: 20px; }
.page-title { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 20px; }
</style>
