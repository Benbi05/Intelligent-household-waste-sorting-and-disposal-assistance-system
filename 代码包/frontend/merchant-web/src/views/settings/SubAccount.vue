<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">子账号管理</h2>
      <el-button type="primary" @click="openCreate"><el-icon><Plus /></el-icon>新增子账号</el-button>
    </div>

    <div class="page-card">
      <DataTable :data="list" :loading="loading" action-width="100">
        <el-table-column prop="username" label="用户名" min-width="140" />
        <el-table-column prop="displayName" label="显示名称" min-width="140" />
        <template #actions="{ row }">
          <el-popconfirm title="确定删除该子账号？" @confirm="handleDelete(row.id)">
            <template #reference><el-button type="danger" link size="small">删除</el-button></template>
          </el-popconfirm>
        </template>
      </DataTable>
      <el-empty v-if="!list.length && !loading" description="暂无子账号" />
    </div>

    <!-- 新增弹窗 -->
    <el-dialog v-model="dialogVisible" title="新增子账号" width="440px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="用户名" prop="username"><el-input v-model="form.username" placeholder="店员登录名" /></el-form-item>
        <el-form-item label="密码" prop="password"><el-input v-model="form.password" type="password" placeholder="至少6位" show-password /></el-form-item>
        <el-form-item label="显示名称"><el-input v-model="form.displayName" placeholder="如：店员小王" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getSubAccounts, createSubAccount, deleteSubAccount } from '@/api/account'
import DataTable from '@/components/table/DataTable.vue'

const list = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)
const formRef = ref(null)
const form = reactive({ username: '', password: '', displayName: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '至少6位', trigger: 'blur' }],
}

async function fetchList() {
  loading.value = true
  try { const r = await getSubAccounts(); list.value = r.data || [] } catch {}
  loading.value = false
}

function openCreate() {
  form.username = ''; form.password = ''; form.displayName = ''
  dialogVisible.value = true
}

async function handleCreate() {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }
  saving.value = true
  try { await createSubAccount({ username: form.username, password: form.password, displayName: form.displayName || form.username }); ElMessage.success('创建成功'); dialogVisible.value = false; fetchList() } catch {}
  saving.value = false
}

async function handleDelete(id) {
  try { await deleteSubAccount(id); ElMessage.success('已删除'); fetchList() } catch {}
}

fetchList()
</script>

<style scoped>
.page-container { padding: 20px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.page-title { font-size: 20px; font-weight: 700; color: #303133; margin: 0; }
</style>
