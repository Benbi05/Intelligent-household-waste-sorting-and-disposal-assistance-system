<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">商品管理</h2>
      <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon>上架商品</el-button>
    </div>

    <el-row :gutter="16" class="stat-row">
      <el-col :span="8"><StatCard label="上架中" :value="stats.onCount || 0" unit="件" color="#67c23a" /></el-col>
      <el-col :span="8"><StatCard label="已下架" :value="stats.offCount || 0" unit="件" color="#909399" /></el-col>
      <el-col :span="8"><StatCard label="本月兑换" :value="totalExchanged" unit="次" color="#1a73e8" /></el-col>
    </el-row>

    <div class="page-card">
      <SearchBar v-model="keyword" placeholder="搜索商品名称" @search="fetchList" />
      <DataTable :data="list" :loading="loading" action-width="160">
        <el-table-column prop="commodityName" label="商品名称" min-width="140" />
        <el-table-column prop="pointPrice" label="积分价格" width="110" align="center">
          <template #default="{ row }"><span class="num">{{ row.pointPrice }} 分</span></template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="90" align="center" />
        <el-table-column prop="monthExchangeCount" label="本月兑换" width="90" align="center" />
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }"><StatusTag :status="row.status==='on'?'enable':'disable'" /></template>
        </el-table-column>
        <template #actions="{ row }">
          <el-button type="primary" link size="small" @click="openDialog(row)">编辑</el-button>
          <el-button v-if="row.status==='on'" type="warning" link size="small" @click="toggleStatus(row,'off')">下架</el-button>
          <el-button v-else type="success" link size="small" @click="toggleStatus(row,'on')">上架</el-button>
        </template>
      </DataTable>
      <Pagination :total="total" v-model:page="page" v-model:size="size" @change="fetchList" />
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit?'编辑商品':'上架商品'" width="580px" :close-on-click-modal="false">
      <!-- 常用物品快捷选择（仅新增时显示） -->
      <div v-if="!isEdit" style="margin-bottom:16px">
        <div style="font-size:13px;color:#909399;margin-bottom:8px">常用物品 · 点击快速填入</div>
        <div class="preset-grid">
          <div v-for="item in presetItems" :key="item.name" class="preset-item" @click="selectPreset(item)">
            <span class="preset-icon">{{ item.icon }}</span>
            <span class="preset-name">{{ item.name }}</span>
            <span class="preset-points">{{ item.points }}分</span>
          </div>
        </div>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="商品名称" prop="commodityName"><el-input v-model="form.commodityName" placeholder="如：垃圾袋50只装" /></el-form-item>
        <el-form-item label="积分价格" prop="pointPrice"><el-input-number v-model="form.pointPrice" :min="1" :max="99999" /></el-form-item>
        <el-form-item label="库存" prop="stock"><el-input-number v-model="form.stock" :min="0" :max="99999" /></el-form-item>
        <el-form-item label="商品描述"><el-input v-model="form.description" type="textarea" :rows="2" placeholder="商品描述（选填）" /></el-form-item>
        <el-form-item label="使用规则"><el-input v-model="form.useRules" placeholder="如：每人限兑1件/月" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getCommodities, createCommodity, updateCommodity } from '@/api/commodity'
import DataTable from '@/components/table/DataTable.vue'
import SearchBar from '@/components/search-bar/SearchBar.vue'
import Pagination from '@/components/pagination/Pagination.vue'
import StatusTag from '@/components/status-tag/StatusTag.vue'
import StatCard from '@/components/stat-card/StatCard.vue'

const list = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const loading = ref(false)
const keyword = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const formRef = ref(null)
const form = reactive({ id: null, commodityName: '', pointPrice: 100, stock: 100, description: '', useRules: '' })
const rules = { commodityName: [{ required: true, message: '请输入商品名称' }], pointPrice: [{ required: true }] }

const presetItems = [
  { icon: '🗑️', name: '垃圾袋（50只装）', points: 50 },
  { icon: '🧻', name: '抽纸（3包装）', points: 80 },
  { icon: '🧴', name: '洗洁精（500ml）', points: 120 },
  { icon: '🫧', name: '洗衣液（1kg）', points: 200 },
  { icon: '🧼', name: '香皂（3块装）', points: 60 },
  { icon: '🪥', name: '牙刷（2支装）', points: 40 },
  { icon: '🧂', name: '食用盐（5包装）', points: 30 },
  { icon: '🍚', name: '大米（2.5kg）', points: 300 },
  { icon: '🫒', name: '食用油（1.8L）', points: 350 },
  { icon: '🥛', name: '纯牛奶（12盒）', points: 260 },
  { icon: '🍜', name: '方便面（5连包）', points: 70 },
  { icon: '🧃', name: '饮料（6瓶装）', points: 90 },
  { icon: '🧹', name: '扫把簸箕套装', points: 150 },
  { icon: '🪣', name: '塑料水桶', points: 100 },
  { icon: '🔋', name: '电池（10粒装）', points: 50 },
  { icon: '🧤', name: '橡胶手套（2双装）', points: 45 },
  { icon: '🕯️', name: '蜡烛（10支装）', points: 25 },
  { icon: '📦', name: '保鲜膜（2卷装）', points: 55 },
  { icon: '🧊', name: '密封袋（50只装）', points: 40 },
  { icon: '🪴', name: '绿植盆栽（小）', points: 180 },
]

function selectPreset(item) {
  form.commodityName = item.name
  form.pointPrice = item.points
  form.stock = 100
}

const stats = computed(() => {
  const onCount = list.value.filter(c => c.status === 'on').length
  const offCount = list.value.filter(c => c.status === 'off').length
  return { onCount, offCount }
})

const totalExchanged = computed(() => list.value.reduce((s, c) => s + (c.monthExchangeCount || 0), 0))

async function fetchList() {
  loading.value = true
  try { const r = await getCommodities({ page: page.value, size: size.value, keyword: keyword.value }); list.value = r.data.records || []; total.value = r.data.total || 0 } catch {}
  loading.value = false
}

function openDialog(row) {
  if (row) {
    isEdit.value = true; form.id = row.id; form.commodityName = row.commodityName; form.pointPrice = row.pointPrice; form.stock = row.stock; form.description = row.description || ''; form.useRules = row.useRules || ''
  } else {
    isEdit.value = false; form.id = null; form.commodityName = ''; form.pointPrice = 100; form.stock = 100; form.description = ''; form.useRules = ''
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }
  saving.value = true
  try {
    const data = { commodityName: form.commodityName, pointPrice: form.pointPrice, stock: form.stock, description: form.description, useRules: form.useRules }
    if (isEdit.value) { await updateCommodity(form.id, data); ElMessage.success('更新成功') }
    else { await createCommodity(data); ElMessage.success('上架成功') }
    dialogVisible.value = false
    fetchList()
  } catch {}
  saving.value = false
}

async function toggleStatus(row, status) {
  try { await updateCommodity(row.id, { status }); ElMessage.success(status === 'on' ? '已上架' : '已下架'); fetchList() } catch {}
}

fetchList()
</script>

<style scoped>
.page-container { padding: 20px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.page-title { font-size: 20px; font-weight: 700; color: #303133; margin: 0; }
.stat-row { margin-bottom: 16px; }
.page-card { margin-top: 0; }
.num { font-weight: 700; color: #303133; }
.preset-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
.preset-item { display: flex; flex-direction: column; align-items: center; padding: 8px 4px; border: 1px solid #ebeef5; border-radius: 8px; cursor: pointer; transition: all .2s; background: #fafbfc; }
.preset-item:hover { border-color: #409eff; background: #ecf5ff; transform: translateY(-1px); }
.preset-icon { font-size: 22px; margin-bottom: 2px; }
.preset-name { font-size: 11px; color: #606266; text-align: center; line-height: 1.3; }
.preset-points { font-size: 11px; color: #e6a23c; font-weight: 600; }
</style>
