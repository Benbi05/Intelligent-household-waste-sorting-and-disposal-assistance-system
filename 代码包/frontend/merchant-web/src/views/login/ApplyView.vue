<template>
  <div class="apply-wrapper">
    <div class="apply-card">
      <h2>商家入驻申请</h2>
      <p class="subtitle">填写店铺信息，提交后等待管理员审核</p>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px" size="large" style="margin-top:32px">
        <el-form-item label="店铺名称" prop="storeName"><el-input v-model="form.storeName" placeholder="如：好邻居便利店" maxlength="64" /></el-form-item>
        <el-form-item label="联系人" prop="contactName"><el-input v-model="form.contactName" placeholder="如：王大姐" maxlength="32" /></el-form-item>
        <el-form-item label="手机号" prop="contactPhone"><el-input v-model="form.contactPhone" placeholder="用于登录" maxlength="11" /></el-form-item>
        <el-form-item label="所在区域" prop="area">
          <el-select v-model="form.area" placeholder="请选择" style="width:100%">
            <el-option v-for="c in communities" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="登录密码" prop="password"><el-input v-model="form.password" type="password" placeholder="至少6位" show-password /></el-form-item>
        <el-form-item label="确认密码" prop="password2"><el-input v-model="form.password2" type="password" placeholder="再次输入密码" show-password /></el-form-item>
        <el-form-item><el-button type="primary" :loading="loading" @click="handleSubmit" style="width:100%">提交申请</el-button></el-form-item>
      </el-form>
      <div class="form-footer">已有账号？<router-link to="/login" class="link">返回登录</router-link></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { apply } from '@/api/auth'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const communities = ['虎溪花园', '学府悦园', '康居西城', '龙湖U城', '金科廊桥水乡', '富力城', '恒大未来城', '融创文旅城']
const form = reactive({ storeName: '', contactName: '', contactPhone: '', area: '', password: '', password2: '' })

const rules = {
  storeName: [{ required: true, message: '请输入店铺名称', trigger: 'blur' }],
  contactName: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  contactPhone: [{ required: true, message: '请输入手机号', trigger: 'blur' }, { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码至少6位', trigger: 'blur' }],
  password2: [{ required: true, message: '请确认密码', trigger: 'blur' }, { validator: (r, v, cb) => cb(v !== form.password ? new Error('两次密码不一致') : undefined), trigger: 'blur' }],
}

async function handleSubmit() {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }
  loading.value = true
  try {
    await apply({ storeName: form.storeName, contactName: form.contactName, contactPhone: form.contactPhone, area: form.area, password: form.password })
    ElMessage.success('申请已提交，请等待管理员审核')
    router.push('/login')
  } catch { /* handled */ }
  loading.value = false
}
</script>

<style scoped>
.apply-wrapper { width: 100%; min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #f0f2f5 0%, #e8eaed 100%); }
.apply-card { width: 520px; padding: 40px; background: #fff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.08); }
.apply-card h2 { font-size: 24px; font-weight: 700; color: #303133; margin: 0; }
.subtitle { font-size: 14px; color: #909399; margin: 8px 0 0; }
.form-footer { text-align: center; font-size: 14px; color: #909399; margin-top: 8px; }
.form-footer .link { color: #67c23a; text-decoration: none; font-weight: 500; }
</style>
