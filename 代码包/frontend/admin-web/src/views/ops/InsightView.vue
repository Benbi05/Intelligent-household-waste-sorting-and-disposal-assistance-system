<template>
  <div class="detail-page">
    <div class="page-header"><h2>消费洞察分析</h2><p class="subtitle">基于投放数据推断各社区消费趋势，指导商家进货策略</p></div>

    <!-- 全区Top品类 -->
    <el-card shadow="never" style="margin-bottom:16px" v-loading="loading">
      <template #header><span class="section-title">全区消费热力图 — {{ data.month }}</span></template>
      <div class="product-grid">
        <div v-for="(p, i) in data.overall" :key="p.category" class="product-tag" :style="{ background: heatColor(i) }">
          <div class="pt-cat">{{ p.category }}</div>
          <div class="pt-prod">→ {{ p.product }}</div>
          <div class="pt-cnt">{{ p.count }}次</div>
        </div>
      </div>
    </el-card>

    <!-- 各社区洞察 -->
    <el-card shadow="never" v-loading="loading">
      <template #header><span class="section-title">各社区消费画像 & 进货建议</span></template>
      <el-row :gutter="16">
        <el-col :span="6" v-for="c in data.communities" :key="c.community" style="margin-bottom:16px">
          <el-card shadow="hover" class="comm-card">
            <template #header><span class="comm-name">{{ c.community }}</span><el-tag size="small" style="margin-left:8px">{{ c.totalDeliveries }}次投放</el-tag></template>
            <div v-if="c.topProducts && c.topProducts.length">
              <div class="suggest-title">建议多备货：</div>
              <div v-for="p in c.topProducts" :key="p.category" class="suggest-item">
                <span class="si-cat">{{ p.category }}</span>
                <span class="si-arrow">→</span>
                <span class="si-prod">{{ p.product }}</span>
                <span class="si-ratio">{{ p.ratio }}%</span>
              </div>
            </div>
            <el-empty v-else description="暂无数据" :image-size="40" />
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/api/request'

const data = ref({ overall: [], communities: [], month: '' })
const loading = ref(true)

function heatColor(i) {
  const colors = ['#1a73e8','#2e7d32','#ef6c00','#1565c0','#c62828','#4527a0','#00695c','#e65100','#283593','#558b2f']
  return colors[i] || '#78909c'
}

onMounted(async () => {
  try { const r = await request.get('/admin/ops/insights'); data.value = r.data } catch {}
  loading.value = false
})
</script>

<style scoped>
.detail-page { padding: 24px; }
.page-header { margin-bottom: 20px; }
.page-header h2 { font-size: 20px; font-weight: 700; color: #303133; margin: 0 0 6px; }
.subtitle { font-size: 13px; color: #909399; margin: 0; }
.section-title { font-size: 14px; font-weight: 600; color: #303133; }
.product-grid { display: flex; flex-wrap: wrap; gap: 10px; }
.product-tag { padding: 12px 16px; border-radius: 10px; color: #fff; min-width: 120px; }
.pt-cat { font-size: 13px; opacity: 0.9; }
.pt-prod { font-size: 15px; font-weight: 700; margin: 4px 0; }
.pt-cnt { font-size: 11px; opacity: 0.8; }
.comm-card { height: 100%; }
.comm-name { font-size: 14px; font-weight: 600; color: #303133; }
.suggest-title { font-size: 12px; color: #e6a23c; font-weight: 600; margin-bottom: 8px; }
.suggest-item { display: flex; align-items: center; gap: 6px; padding: 6px 0; border-bottom: 1px solid #f5f7fa; font-size: 13px; }
.si-cat { color: #606266; flex: 1; }
.si-arrow { color: #c0c4cc; }
.si-prod { color: #1a73e8; font-weight: 600; flex: 1; }
.si-ratio { color: #909399; font-size: 11px; }
</style>
