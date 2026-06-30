<template>
  <div class="page-container">
    <h2 class="page-title">店铺设置</h2>
    <div class="page-card" style="max-width:600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" v-loading="loading">
        <el-form-item label="店铺名称" prop="storeName"><el-input v-model="form.storeName" /></el-form-item>
        <el-form-item label="店铺地址"><el-input v-model="form.storeAddress" placeholder="请填写店铺详细地址" /></el-form-item>
        <el-form-item label="联系人" prop="contactName"><el-input v-model="form.contactName" /></el-form-item>
        <el-form-item label="联系电话" prop="contactPhone"><el-input v-model="form.contactPhone" /></el-form-item>
        <el-form-item label="所在区域"><el-input v-model="form.area" disabled /></el-form-item>
        <el-form-item label="店铺简介"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item><el-button type="primary" :loading="saving" @click="handleSave">保存修改</el-button></el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getShopInfo, updateShopInfo } from '@/api/auth'

const formRef = ref(null)
const loading = ref(true)
const saving = ref(false)
const form = reactive({ storeName: '', storeAddress: '', contactName: '', contactPhone: '', area: '', description: '' })
const rules = {
  storeName: [{ required: true, message: '请输入店铺名称' }],
  contactName: [{ required: true, message: '请输入联系人' }],
  contactPhone: [{ required: true, message: '请输入联系电话' }],
}

onMounted(async () => {
  try { const r = await getShopInfo(); Object.assign(form, r.data) } catch {}
  loading.value = false
})

async function handleSave() {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }
  saving.value = true
  try { await updateShopInfo({ storeName: form.storeName, storeAddress: form.storeAddress, contactName: form.contactName, contactPhone: form.contactPhone, description: form.description }); ElMessage.success('保存成功') } catch {}
  saving.value = false
}
</script>

<style scoped>
.page-container { padding: 20px; }
.page-title { font-size: 20px; font-weight: 700; color: #303133; margin-bottom: 20px; }
</style>
