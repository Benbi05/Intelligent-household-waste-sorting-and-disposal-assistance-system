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
    <el-dialog v-model="dialogVisible" :title="isEdit?'编辑商品':'上架商品'" width="520px" :close-on-click-modal="false">
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
</style>
