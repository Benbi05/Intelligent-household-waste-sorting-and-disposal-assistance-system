<template>
  <div class="detail-page">
    <div class="page-header">
      <h2>数据统计与报表导出</h2>
      <p class="subtitle">选择报表模板，系统自动生成 Excel 文件下载</p>
    </div>

    <el-row :gutter="20" style="margin-bottom:24px">
      <el-col :span="6" v-for="tpl in templates" :key="tpl.key">
        <el-card shadow="hover" class="tpl-card" @click="exportReport(tpl.key)">
          <div class="tpl-icon">{{ tpl.icon }}</div>
          <div class="tpl-name">{{ tpl.name }}</div>
          <div class="tpl-desc">{{ tpl.desc }}</div>
          <el-button type="primary" size="small" :loading="loadingKey === tpl.key" style="margin-top:10px">
            {{ loadingKey === tpl.key ? '生成中...' : '导出 Excel' }}
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-divider content-position="left">实时概览</el-divider>
    <el-row :gutter="16">
      <el-col :span="6" v-for="s in summaryCards" :key="s.label">
        <div class="sum-card">
          <div class="sum-val" :style="{ color: s.color }">{{ s.value }}</div>
          <div class="sum-label">{{ s.label }}</div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'
import { getOverview } from '@/api/statistics'
import request from '@/api/request'

const userStore = useUserStore()
const comm = computed(() => userStore.community || '')
const overview = ref({})
const loadingKey = ref('')

const templates = [
  { key: 'monthly', icon: '📊', name: '月度分类报告', desc: '本月各社区投放总量、正确率、积分汇总' },
  { key: 'delivery', icon: '📋', name: '投放数据明细', desc: '30天全部投放记录，含设备、品类、正误' },
  { key: 'device', icon: '🔧', name: '设备状态报表', desc: '所有设备在线状态、满溢度、最后在线时间' },
  { key: 'community', icon: '🏘️', name: '社区对比报表', desc: '8个社区投放量、正确率、用户数一览表' },
]

const summaryCards = computed(() => [
  { label: '总投放次数', value: overview.value.monthDeliveryCount || 0, color: '#1a73e8' },
  { label: '分类正确率', value: (overview.value.monthCorrectRate ? (overview.value.monthCorrectRate*100).toFixed(1) : 0) + '%', color: '#2e7d32' },
  { label: '在线设备', value: overview.value.onlineDevices || 0, color: '#ef6c00' },
  { label: '注册用户', value: overview.value.totalUsers || 0, color: '#78909c' },
])

onMounted(async () => {
  try { const r = await getOverview(comm.value ? { community: comm.value } : {}); overview.value = r.data } catch {}
})

async function exportReport(key) {
  loadingKey.value = key
  try {
    const c = comm.value ? '&community=' + comm.value : ''
    const urls = {
      monthly: '/admin/statistics/export?type=monthly' + c,
      delivery: '/admin/statistics/export?type=delivery' + c,
      device: '/admin/statistics/export?type=device',
      community: '/admin/statistics/export?type=community',
    }
    const res = await request.get(urls[key] || '/admin/statistics/export')
    if (res.data?.exportUrl) {
      ElMessage.success('报表生成成功，正在下载')
      let url = res.data.exportUrl
      const host = localStorage.getItem('backend_host')
      if (host) url = 'http://' + host + ':8082' + url
      const a = document.createElement('a')
      a.href = url
      a.download = (res.data.reportName || '报表') + '.xlsx'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    }
  } catch { ElMessage.error('生成失败') }
  loadingKey.value = ''
}
</script>

<style scoped>
.detail-page { padding: 24px; max-width: none; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 20px; font-weight: 700; color: #303133; margin: 0 0 6px; }
.subtitle { font-size: 13px; color: #909399; margin: 0; }
.tpl-card { text-align: center; cursor: pointer; border-radius: 10px; transition: all .2s; }
.tpl-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
.tpl-icon { font-size: 36px; margin-bottom: 8px; }
.tpl-name { font-size: 15px; font-weight: 600; color: #303133; margin-bottom: 4px; }
.tpl-desc { font-size: 12px; color: #909399; }
.sum-card { text-align: center; padding: 20px; border-radius: 10px; background: #f5f7fa; }
.sum-val { font-size: 28px; font-weight: 700; }
.sum-label { font-size: 13px; color: #909399; margin-top: 6px; }
</style>
