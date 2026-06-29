<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title" style="margin-bottom: 0">区域管理</h2>
      <el-button type="primary" @click="openAddDialog">
        <el-icon><Plus /></el-icon>新增区域
      </el-button>
    </div>

    <div class="page-card">
      <DataTable :data="areaList" :loading="loading" :action-width="160">
        <el-table-column prop="areaId" label="区域ID" width="80" align="center" />
        <el-table-column prop="areaName" label="区域名称" min-width="150" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">{{ row.description || '-' }}</template>
        </el-table-column>
        <el-table-column prop="deviceCount" label="设备数量" width="100" align="center" />
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <StatusTag :status="row.status" />
          </template>
        </el-table-column>

        <template #actions="{ row }">
          <el-button type="primary" link size="small" @click="openEditDialog(row)">编辑</el-button>
          <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </DataTable>
    </div>

    <!-- 新增/编辑弹窗 -->
    <FormDialog
      v-model="dialogVisible"
      :title="dialogTitle"
      :form-data="formData"
      :rules="formRules"
      :submitting="submitting"
      @confirm="handleSubmit"
    >
      <template #default>
        <el-form-item label="区域名称" prop="areaName">
          <el-input v-model="formData.areaName" placeholder="请输入区域名称" maxlength="64" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入区域描述（选填）"
            maxlength="256"
          />
        </el-form-item>
      </template>
    </FormDialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getAreaList, createArea, updateArea, deleteArea } from '@/api/area'
import DataTable from '@/components/table/DataTable.vue'
import FormDialog from '@/components/form-dialog/FormDialog.vue'
import StatusTag from '@/components/status-tag/StatusTag.vue'

const loading = ref(false)
const areaList = ref([])

// 弹窗相关
const dialogVisible = ref(false)
const dialogTitle = ref('新增区域')
const isEdit = ref(false)
const editAreaId = ref(null)
const submitting = ref(false)

const formData = reactive({ areaName: '', description: '' })
const formRules = {
  areaName: [{ required: true, message: '请输入区域名称', trigger: 'blur' }],
}

async function fetchAreas() {
  loading.value = true
  try {
    const res = await getAreaList()
    areaList.value = res.data || []
  } catch {
    // handled in request interceptor
  } finally {
    loading.value = false
  }
}

function openAddDialog() {
  isEdit.value = false
  editAreaId.value = null
  dialogTitle.value = '新增区域'
  formData.areaName = ''
  formData.description = ''
  dialogVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  editAreaId.value = row.areaId
  dialogTitle.value = '编辑区域'
  formData.areaName = row.areaName
  formData.description = row.description || ''
  dialogVisible.value = true
}

async function handleSubmit() {
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateArea(editAreaId.value, { ...formData })
      ElMessage.success('更新成功')
    } else {
      await createArea({ ...formData })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchAreas()
  } catch {
    // handled in request interceptor
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除区域「${row.areaName}」吗？${row.deviceCount > 0 ? `该区域下有 ${row.deviceCount} 台设备，删除后设备将变为未分配。` : ''}`,
      '删除确认',
      {
        type: 'error',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
      }
    )
  } catch {
    return
  }

  try {
    await deleteArea(row.areaId)
    ElMessage.success('删除成功')
    fetchAreas()
  } catch {
    // handled in request interceptor
  }
}

// 初始加载
fetchAreas()
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
</style>
