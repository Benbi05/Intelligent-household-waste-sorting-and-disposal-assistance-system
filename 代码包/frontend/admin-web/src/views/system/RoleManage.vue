<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title" style="margin-bottom: 0">角色管理</h2>
      <el-button type="primary" @click="openAddDialog">
        <el-icon><Plus /></el-icon>新增角色
      </el-button>
    </div>

    <div class="page-card">
      <DataTable :data="roleList" :loading="loading" :action-width="180">
        <el-table-column prop="roleId" label="角色ID" width="80" align="center" />
        <el-table-column prop="roleName" label="角色名称" min-width="130" />
        <el-table-column prop="permissions" label="权限列表" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tag v-for="p in parsePermissions(row.permissions)" :key="p" size="small" style="margin:2px">{{ p }}</el-tag>
            <span v-if="!row.permissions" class="tip-text">未设置</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">{{ row.description || '-' }}</template>
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
        <el-form-item label="角色名称" prop="roleName">
          <el-input v-model="formData.roleName" placeholder="请输入角色名称" maxlength="64" />
        </el-form-item>
        <el-form-item label="权限列表" prop="permissions">
          <el-input v-model="formData.permissions" placeholder="多个权限用英文逗号分隔" maxlength="256" />
          <div class="form-tip">例如：user:read,user:write,device:read</div>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入角色描述" maxlength="256" />
        </el-form-item>
      </template>
    </FormDialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getRoleList, createRole, updateRole, deleteRole } from '@/api/role'
import DataTable from '@/components/table/DataTable.vue'
import FormDialog from '@/components/form-dialog/FormDialog.vue'

const loading = ref(false)
const roleList = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('新增角色')
const isEdit = ref(false)
const editRoleId = ref(null)
const submitting = ref(false)

const formData = reactive({ roleName: '', permissions: '', description: '' })
const formRules = { roleName: [{ required: true, message: '请输入角色名称', trigger: 'blur' }] }

async function fetchRoles() {
  loading.value = true
  try {
    const res = await getRoleList()
    roleList.value = res.data || []
  } catch { /* handled */ } finally { loading.value = false }
}

function openAddDialog() {
  isEdit.value = false; editRoleId.value = null; dialogTitle.value = '新增角色'
  formData.roleName = ''; formData.permissions = ''; formData.description = ''
  dialogVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true; editRoleId.value = row.roleId; dialogTitle.value = '编辑角色'
  formData.roleName = row.roleName; formData.permissions = row.permissions || ''; formData.description = row.description || ''
  dialogVisible.value = true
}

async function handleSubmit() {
  submitting.value = true
  try {
    const data = { roleName: formData.roleName, permissions: formData.permissions, description: formData.description }
    if (isEdit.value) {
      await updateRole(editRoleId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createRole(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchRoles()
  } catch { /* handled */ } finally { submitting.value = false }
}

async function handleDelete(row) {
  try { await ElMessageBox.confirm(`确定要删除角色「${row.roleName}」吗？`, '删除确认', { type: 'error' }) } catch { return }
  try { await deleteRole(row.roleId); ElMessage.success('删除成功'); fetchRoles() } catch { /* handled */ }
}

function parsePermissions(str) {
  if (!str) return []
  return str.split(',').map(s => s.trim()).filter(Boolean)
}

fetchRoles()
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.tip-text { font-size: 12px; color: #c0c4cc; }
.form-tip { font-size: 12px; color: #909399; margin-top: 4px; }
</style>
