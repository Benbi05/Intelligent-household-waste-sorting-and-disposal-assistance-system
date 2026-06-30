<template>
  <div class="detail-page">
    <div class="page-header">
      <h2>AI模型管理</h2>
      <el-button type="primary" @click="publishVisible = true"><el-icon><Plus /></el-icon>发布新版本</el-button>
    </div>

    <el-card shadow="never" v-loading="loading">
      <el-table :data="models" stripe size="medium">
        <el-table-column prop="version" label="版本" width="100" />
        <el-table-column prop="accuracy" label="准确率" width="100" align="center">
          <template #default="{row}">{{ row.accuracy }}%</template>
        </el-table-column>
        <el-table-column prop="mapValue" label="mAP" width="80" align="center">
          <template #default="{row}">{{ row.mapValue }}%</template>
        </el-table-column>
        <el-table-column prop="precision" label="精确率" width="80" align="center">
          <template #default="{row}">{{ row.precision }}%</template>
        </el-table-column>
        <el-table-column prop="recall" label="召回率" width="80" align="center">
          <template #default="{row}">{{ row.recall }}%</template>
        </el-table-column>
        <el-table-column prop="categoryCount" label="品类数" width="80" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{row}">
            <el-tag :type="row.status==='active'?'success':'info'" size="small">{{ row.status==='active'?'运行中':'离线' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="publishTime" label="发布时间" width="170">
          <template #default="{row}">{{ (row.publishTime||'').slice(0,16).replace('T',' ') }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="{row}">
            <el-button v-if="row.status !== 'active'" type="primary" link size="small" @click="handleSwitch(row)" :loading="switching===row.modelId">切换至此版本</el-button>
            <el-tag v-else type="success" size="small">当前版本</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!models.length" description="暂无模型，请发布第一个版本" />
    </el-card>

    <el-dialog v-model="publishVisible" title="发布新模型版本" width="460px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="版本号" prop="version"><el-input v-model="form.version" placeholder="如 v2.0" /></el-form-item>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="准确率"><el-input-number v-model="form.accuracy" :min="0" :max="100" style="width:100%" />%</el-form-item></el-col>
          <el-col :span="12"><el-form-item label="mAP"><el-input-number v-model="form.mapValue" :min="0" :max="100" style="width:100%" />%</el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="精确率"><el-input-number v-model="form.precision" :min="0" :max="100" style="width:100%" />%</el-form-item></el-col>
          <el-col :span="12"><el-form-item label="召回率"><el-input-number v-model="form.recall" :min="0" :max="100" style="width:100%" />%</el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="publishVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handlePublish">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request'

const models = ref([])
const loading = ref(true)
const publishVisible = ref(false)
const saving = ref(false)
const switching = ref(null)
const formRef = ref(null)
const form = reactive({ version: '', accuracy: 90, mapValue: 85, precision: 88, recall: 82 })
const rules = { version: [{ required: true, message: '请输入版本号' }] }

async function fetchModels() {
  loading.value = true
  try { const r = await request.get('/admin/models'); models.value = r.data } catch {}
  loading.value = false
}

async function handlePublish() {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }
  saving.value = true
  try {
    await request.post('/admin/models/publish', {
      version: form.version, accuracy: form.accuracy / 100, mapValue: form.mapValue / 100,
      precision: form.precision / 100, recall: form.recall / 100,
    })
    ElMessage.success('模型版本发布成功')
    publishVisible.value = false
    form.version = ''
    fetchModels()
  } catch {}
  saving.value = false
}

async function handleSwitch(row) {
  try { await ElMessageBox.confirm(`确定将AI模型切换至 ${row.version}？`, '切换确认', { type: 'warning' }) } catch { return }
  switching.value = row.modelId
  try { await request.post(`/admin/models/${row.modelId}/switch`); ElMessage.success(`已切换至 ${row.version}`); fetchModels() } catch {}
  switching.value = null
}

fetchModels()
</script>

<style scoped>
.detail-page { padding: 24px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.page-header h2 { font-size: 20px; font-weight: 700; color: #303133; margin: 0; }
</style>
