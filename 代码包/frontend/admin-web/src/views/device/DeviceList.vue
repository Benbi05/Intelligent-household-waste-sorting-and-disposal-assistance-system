<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title" style="margin-bottom: 0">设备管理</h2>
      <el-button type="primary" @click="openAddDialog">
        <el-icon><Plus /></el-icon>新增设备
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6"><StatCard label="在线" :value="deviceStats.online || 0" unit="台" color="#67c23a" /></el-col>
      <el-col :span="6"><StatCard label="离线" :value="deviceStats.offline || 0" unit="台" color="#909399" /></el-col>
      <el-col :span="6"><StatCard label="故障" :value="deviceStats.fault || 0" unit="台" color="#f56c6c" /></el-col>
      <el-col :span="6"><StatCard label="待检测" :value="deviceStats.pending || 0" unit="台" color="#e6a23c" /></el-col>
    </el-row>

    <!-- 筛选栏 -->
    <div style="margin-bottom:16px;display:flex;gap:12px;align-items:center">
      <el-button :type="filterFull ? 'danger' : ''" size="small" @click="filterFull=!filterFull;pagination.page=1;fetchDevices()">
        🗑️ 满溢告警 (≥85%)
      </el-button>
      <el-select v-model="searchForm.status" placeholder="在线状态" clearable style="width:140px" @change="pagination.page=1;fetchDevices()">
        <el-option label="在线" value="online" />
        <el-option label="离线" value="offline" />
        <el-option label="故障" value="fault" />
        <el-option label="待检测" value="pending_check" />
      </el-select>
      <el-select v-model="searchForm.boxCategory" placeholder="设备分类" clearable style="width:140px" @change="pagination.page=1;fetchDevices()">
        <el-option label="可回收物" value="recyclable" />
        <el-option label="厨余垃圾" value="kitchen" />
        <el-option label="有害垃圾" value="harmful" />
        <el-option label="其他垃圾" value="other" />
      </el-select>
    </div>

    <!-- 数据表格 -->
    <div class="page-card">
      <DataTable :data="tableData" :action-width="200" show-selection @selection-change="onSelectChange">
        <el-table-column prop="deviceId" label="设备ID" width="150" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            <span :style="{ color: (row.fullRate || 0) >= 85 ? '#f56c6c' : '', fontWeight: (row.fullRate || 0) >= 85 ? '700' : '' }">{{ row.deviceId }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="deviceName" label="设备名称" min-width="130" show-overflow-tooltip />
        <el-table-column prop="boxCategory" label="分类" width="100" align="center">
          <template #default="{ row }">{{ catLabel(row.boxCategory) }}</template>
        </el-table-column>
        <el-table-column prop="onlineStatus" label="在线状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.onlineStatus==='online'" type="success" size="small">在线</el-tag>
            <el-tag v-else-if="row.onlineStatus==='fault'" type="danger" size="small">故障</el-tag>
            <el-tag v-else-if="row.onlineStatus==='pending_check'" type="warning" size="small">待检测</el-tag>
            <el-tag v-else type="info" size="small">离线</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fullRate" label="满溢率" width="90" align="center" sortable>
          <template #default="{ row }">
            <span :style="{ color: (row.fullRate || 0) >= 85 ? '#f56c6c' : '', fontWeight: (row.fullRate || 0) >= 85 ? '700' : '' }">{{ row.fullRate ?? '-' }}{{ row.fullRate != null ? '%' : '' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }"><StatusTag :status="row.status" /></template>
        </el-table-column>
        <el-table-column prop="firmwareVersion" label="固件版本" width="110" align="center" />
        <el-table-column prop="lastOnlineTime" label="最后在线" width="170" align="center">
          <template #default="{ row }">{{ formatTime(row.lastOnlineTime) }}</template>
        </el-table-column>

        <template #actions="{ row }">
          <el-button type="primary" link size="small" @click="openConfigDialog(row)">配置</el-button>
          <el-button v-if="row.status==='enable'" type="danger" link size="small" @click="toggleStatus(row,'disable')">禁用</el-button>
          <el-button v-else type="success" link size="small" @click="toggleStatus(row,'enable')">启用</el-button>
          <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </DataTable>

      <Pagination :total="total" v-model:page="pagination.page" v-model:size="pagination.size" @change="fetchDevices" />
    </div>

    <!-- 新增设备弹窗 -->
    <FormDialog v-model="addDialogVisible" title="新增设备" :form-data="addForm" :rules="addRules" :submitting="submitting" @confirm="handleAdd">
      <template #default>
        <el-form-item label="设备名称" prop="deviceName">
          <el-input v-model="addForm.deviceName" placeholder="请输入设备名称" maxlength="64" />
        </el-form-item>
        <el-form-item label="分类" prop="boxCategory">
          <el-select v-model="addForm.boxCategory" placeholder="请选择分类" style="width:100%">
            <el-option label="可回收物" value="recyclable" />
            <el-option label="厨余垃圾" value="kitchen" />
            <el-option label="有害垃圾" value="harmful" />
            <el-option label="其他垃圾" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="addForm.location" placeholder="请输入位置" maxlength="128" />
        </el-form-item>
      </template>
    </FormDialog>

    <!-- 配置设备弹窗 -->
    <FormDialog v-model="configDialogVisible" title="设备配置" :form-data="configForm" :rules="configRules" :submitting="submitting" @confirm="handleConfig">
      <template #default>
        <el-form-item label="设备名称" prop="deviceName">
          <el-input v-model="configForm.deviceName" placeholder="请输入设备名称" maxlength="64" />
        </el-form-item>
        <el-form-item label="分类" prop="boxCategory">
          <el-select v-model="configForm.boxCategory" placeholder="请选择分类" style="width:100%">
            <el-option label="可回收物" value="recyclable" />
            <el-option label="厨余垃圾" value="kitchen" />
            <el-option label="有害垃圾" value="harmful" />
            <el-option label="其他垃圾" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="configForm.location" placeholder="请输入位置" maxlength="128" />
        </el-form-item>
      </template>
    </FormDialog>

    <!-- 固件升级弹窗 -->
    <el-dialog v-model="firmwareVisible" title="固件升级" width="460px" :close-on-click-modal="false">
      <el-form :model="firmwareForm" label-width="100px">
        <el-form-item label="目标设备">
          <el-tag v-for="id in selectedIds" :key="id" size="small" class="device-tag">{{ id }}</el-tag>
          <span v-if="selectedIds.length === 0" class="tip-text">请先在表格中选择设备</span>
        </el-form-item>
        <el-form-item label="固件版本" required>
          <el-input v-model="firmwareForm.version" placeholder="请输入固件版本号" maxlength="32" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="firmwareVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" :disabled="selectedIds.length === 0 || !firmwareForm.version" @click="handleFirmware">确定升级</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getDeviceList, createDevice, updateDeviceStatus, deleteDevice, updateDeviceConfig, firmwareUpgrade, getDeviceStats } from '@/api/device'
import DataTable from '@/components/table/DataTable.vue'

import Pagination from '@/components/pagination/Pagination.vue'
import FormDialog from '@/components/form-dialog/FormDialog.vue'
import StatusTag from '@/components/status-tag/StatusTag.vue'
import StatCard from '@/components/stat-card/StatCard.vue'

import { useUserStore } from '@/store/user'
const userStore = useUserStore()
const isAdmin = computed(() => userStore.role === 'super_admin')
const comm = computed(() => userStore.community || '')

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const selectedIds = ref([])
const submitting = ref(false)
const deviceStats = ref({})
const filterFull = ref(false)

const searchForm = reactive({ status: '', boxCategory: '' })
const onlineStatusOptions = [
  { label: '在线', value: 'online' },
  { label: '离线', value: 'offline' },
  { label: '故障', value: 'fault' },
  { label: '待检测', value: 'pending_check' },
]

const pagination = reactive({ page: 1, size: 10 })

// 新增弹窗
const addDialogVisible = ref(false)
const addForm = reactive({ deviceName: '', boxCategory: 'recyclable', location: '' })
const addRules = { deviceName: [{ required: true, message: '请输入设备名称', trigger: 'blur' }] }

// 配置弹窗
const configDialogVisible = ref(false)
const configDeviceId = ref('')
const configForm = reactive({ deviceName: '', boxCategory: '', location: '' })
const configRules = { deviceName: [{ required: true, message: '请输入设备名称', trigger: 'blur' }] }

// 固件升级
const firmwareVisible = ref(false)
const firmwareForm = reactive({ version: '' })

const catMap = { recyclable: '可回收物', kitchen: '厨余垃圾', harmful: '有害垃圾', other: '其他垃圾' }
function catLabel(v) { return catMap[v] || v }

function onSelectChange(sel) { selectedIds.value = sel.map(s => s.deviceId) }

async function fetchDevices() {
  try {
    const res = await getDeviceList({
      page: pagination.page, size: pagination.size,
      onlineStatus: searchForm.status,
      boxCategory: searchForm.boxCategory,
      community: comm.value,
      fullRateMin: filterFull.value ? 85 : undefined,
    })
    tableData.value = res.data.records || []
    total.value = res.data.total || 0
  } catch { /* handled */ }
}

function onSearch() { pagination.page = 1; fetchDevices() }
function onReset() { pagination.page = 1; fetchDevices() }

// 新增
function openAddDialog() {
  addForm.deviceName = ''; addForm.boxCategory = 'recyclable'; addForm.location = ''
  addDialogVisible.value = true
}
async function handleAdd() {
  submitting.value = true
  try {
    await createDevice({ ...addForm })
    ElMessage.success('设备创建成功')
    addDialogVisible.value = false
    fetchDevices()
  } catch { /* handled */ } finally { submitting.value = false }
}

// 配置
function openConfigDialog(row) {
  configDeviceId.value = row.deviceId
  configForm.deviceName = row.deviceName; configForm.boxCategory = row.boxCategory
  configForm.location = row.location || ''
  configDialogVisible.value = true
}
async function handleConfig() {
  submitting.value = true
  try {
    await updateDeviceConfig(configDeviceId.value, { ...configForm })
    ElMessage.success('配置更新成功')
    configDialogVisible.value = false
    fetchDevices()
  } catch { /* handled */ } finally { submitting.value = false }
}

// 状态切换
async function toggleStatus(row, status) {
  const act = status === 'enable' ? '启用' : '禁用'
  try { await ElMessageBox.confirm(`确定要${act}设备「${row.deviceName}」吗？`, '操作确认', { type: 'warning' }) } catch { return }
  try { await updateDeviceStatus(row.deviceId, status); ElMessage.success(`${act}成功`); fetchDevices() } catch { /* handled */ }
}

// 删除
async function handleDelete(row) {
  try { await ElMessageBox.confirm(`确定要删除设备「${row.deviceName}」吗？`, '删除确认', { type: 'error' }) } catch { return }
  try { await deleteDevice(row.deviceId); ElMessage.success('删除成功'); fetchDevices() } catch { /* handled */ }
}

// 固件升级
async function handleFirmware() {
  submitting.value = true
  try {
    const res = await firmwareUpgrade(selectedIds.value, firmwareForm.version)
    ElMessage.success(`固件升级指令已下发，影响 ${res.data.affectedDeviceCount} 台设备`)
    firmwareVisible.value = false
  } catch { /* handled */ } finally { submitting.value = false }
}

function formatTime(s) { if (!s) return '-'; return s.replace('T', ' ').substring(0, 19) }

fetchDevices()
fetchDeviceStats()

async function fetchDeviceStats() {
  try { const r = await getDeviceStats(comm.value ? { community: comm.value } : {}); deviceStats.value = r.data } catch {}
}
</script>

<style scoped>
.stat-row { margin-bottom: 16px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.device-tag { margin: 2px; }
.tip-text { font-size: 13px; color: #909399; }
</style>
