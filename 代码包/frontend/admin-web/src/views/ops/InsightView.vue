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
            <div style="margin-top:12px">
              <el-button type="primary" size="small" @click="openPush(c)" :loading="pushing===c.community">
                推送至商家 →
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 推送到商家弹窗 -->
    <el-dialog v-model="pushVisible" title="推送进货建议到商家" width="500px">
      <div style="margin-bottom:12px;font-size:13px;color:#606266">
        社区：<b>{{ pushTarget?.community }}</b> | 建议商品：
        <el-tag v-for="p in pushTarget?.topProducts" :key="p.category" size="small" style="margin:2px">{{ p.product }}</el-tag>
      </div>
      <el-form label-width="80px">
        <el-form-item label="目标商家">
          <el-select v-model="selectedMerchant" placeholder="请选择商家" style="width:100%" filterable>
            <el-option v-for="m in merchants" :key="m.merchantId" :label="m.storeName + ' (' + m.area + ')'" :value="m.merchantId" />
          </el-select>
        </el-form-item>
        <el-form-item label="推送内容">
          <el-input v-model="pushContent" type="textarea" :rows="3" placeholder="自定义推送消息（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pushVisible = false">取消</el-button>
        <el-button type="primary" :loading="pushing" @click="handlePush">确认推送</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const data = ref({ overall: [], communities: [], month: '' })
const loading = ref(true)
const pushVisible = ref(false)
const pushTarget = ref(null)
const selectedMerchant = ref(null)
const pushContent = ref('')
const pushing = ref(null)
const merchants = ref([])

function heatColor(i) {
  const colors = ['#1a73e8','#2e7d32','#ef6c00','#1565c0','#c62828','#4527a0','#00695c','#e65100','#283593','#558b2f']
  return colors[i] || '#78909c'
}

function openPush(community) {
  pushTarget.value = community
  selectedMerchant.value = null
  pushContent.value = ''
  pushVisible.value = true
}

async function handlePush() {
  if (!selectedMerchant.value) { ElMessage.warning('请选择目标商家'); return }
  pushing.value = pushTarget.value?.community
  try {
    await request.post('/admin/ops/insights/push', {
      merchantId: selectedMerchant.value,
      community: pushTarget.value?.community,
      products: pushTarget.value?.topProducts || [],
      content: pushContent.value || `AI消费洞察：${pushTarget.value?.community}本月消费趋势分析`,
    })
    ElMessage.success('推送成功')
    pushVisible.value = false
  } catch {}
  pushing.value = null
}

onMounted(async () => {
  try { const r = await request.get('/admin/ops/insights'); data.value = r.data } catch {}
  // 加载商家列表
  try { const r = await request.get('/admin/merchants', { params: { status: 'approved', size: 50 } }); merchants.value = r.data.records || [] } catch {}
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
