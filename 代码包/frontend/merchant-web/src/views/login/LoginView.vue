<template>
  <div class="login-wrapper">
    <div class="login-bg">
      <div class="bg-shape shape-1"></div><div class="bg-shape shape-2"></div><div class="bg-shape shape-3"></div>
    </div>
    <div class="login-card">
      <div class="login-brand">
        <div class="brand-overlay"></div>
        <div class="brand-content">
          <div class="brand-icon"><svg viewBox="0 0 90 90" fill="none"><circle cx="45" cy="45" r="42" stroke="rgba(255,255,255,0.3)" stroke-width="2"/><path d="M28 44c0-10 10-16 17-12 7-4 17 2 17 12s-10 16-17 12c-7 4-17-2-17-12z" fill="rgba(103,194,58,0.8)"/></svg></div>
          <div class="brand-title">商家后台</div>
          <div class="brand-subtitle">Merchant Portal</div>
          <div class="brand-features">
            <div class="feature-item"><span class="feature-icon">📦</span>商品管理</div>
            <div class="feature-item"><span class="feature-icon">📋</span>订单核销</div>
            <div class="feature-item"><span class="feature-icon">📊</span>经营报表</div>
            <div class="feature-item"><span class="feature-icon">👥</span>子账号</div>
          </div>
        </div>
      </div>
      <div class="login-form-area">
        <div class="form-header"><h2>商家登录</h2><p>积分商城 · 商品管理与订单核销</p></div>
        <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleLogin">
          <el-form-item prop="username"><el-input v-model="form.username" placeholder="用户名" size="large" :prefix-icon="User" /></el-form-item>
          <el-form-item prop="password"><el-input v-model="form.password" type="password" placeholder="密码" size="large" :prefix-icon="Lock" show-password /></el-form-item>
          <el-form-item prop="captchaCode">
            <div class="captcha-row">
              <el-input v-model="form.captchaCode" placeholder="请输入图形验证码" :prefix-icon="Key" size="large" class="captcha-input" maxlength="4" />
              <div class="captcha-img" @click="refreshCaptcha" title="点击刷新">
                <img v-if="captchaImage" :src="captchaImage" alt="验证码" />
                <span v-else>加载中...</span>
              </div>
            </div>
          </el-form-item>
          <el-form-item><el-button type="primary" size="large" style="width:100%" :loading="loading" @click="handleLogin">登 录</el-button></el-form-item>
        </el-form>
        <div class="form-footer">还没有账号？<router-link to="/apply" class="link">申请入驻</router-link></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Key } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store'
import request from '@/api/request'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)
const captchaImage = ref('')
const captchaToken = ref('')
const form = reactive({ username: '', password: '', captchaCode: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captchaCode: [{ required: true, message: '请输入图形验证码', trigger: 'blur' }],
}

async function refreshCaptcha() {
  try {
    const res = await request.get('/common/captcha')
    captchaToken.value = res.data.captchaToken
    captchaImage.value = res.data.captchaImage
    form.captchaCode = ''
  } catch { /* captcha load failed */ }
}

async function handleLogin() {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }
  loading.value = true
  try {
    await userStore.login(form.username, form.password, captchaToken.value, form.captchaCode)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch { refreshCaptcha() }
  loading.value = false
}

onMounted(refreshCaptcha)
</script>

<style scoped>
.login-wrapper { position: relative; width: 100%; height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #0a1628 0%, #1a3a4a 40%, #0d5e3a 100%); overflow: hidden; }
.login-bg { position: absolute; inset: 0; pointer-events: none; z-index: 0; }
.bg-shape { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.15; }
.shape-1 { width: 500px; height: 500px; background: #e6a23c; top: -150px; right: -100px; animation: float1 8s ease-in-out infinite; }
.shape-2 { width: 400px; height: 400px; background: #409eff; bottom: -120px; left: -80px; animation: float2 10s ease-in-out infinite; }
.shape-3 { width: 300px; height: 300px; background: #67c23a; top: 40%; left: 45%; animation: float3 12s ease-in-out infinite; }
@keyframes float1 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(-30px,20px) scale(1.05); } }
@keyframes float2 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(30px,-20px) scale(1.08); } }
@keyframes float3 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(-15px,-15px) scale(1.06); } }
.login-card { position: relative; z-index: 1; display: flex; width: 960px; min-height: 540px; border-radius: 20px; box-shadow: 0 25px 80px rgba(0,0,0,0.35); overflow: hidden; }
.login-brand { width: 420px; flex-shrink: 0; background: linear-gradient(160deg, #1a5a8a 0%, #0d4a7a 30%, #0b3a60 70%, #082a48 100%); display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative; }
.brand-overlay { position: absolute; inset: 0; background: radial-gradient(circle at 20% 80%, rgba(64,158,255,0.2) 0%, transparent 50%), radial-gradient(circle at 70% 20%, rgba(230,162,60,0.15) 0%, transparent 50%); }
.brand-content { position: relative; z-index: 2; text-align: center; padding: 40px 30px; color: #fff; }
.brand-icon { margin-bottom: 24px; }
.brand-title { font-size: 22px; font-weight: 700; line-height: 1.5; margin: 0 0 10px; letter-spacing: 2px; }
.brand-subtitle { font-size: 10px; font-weight: 400; opacity: 0.7; letter-spacing: 1.5px; margin: 0 0 32px; text-transform: uppercase; }
.brand-features { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 10px; }
.feature-item { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: rgba(255,255,255,0.1); border-radius: 10px; font-size: 13px; font-weight: 500; }
.feature-item:hover { background: rgba(255,255,255,0.18); }
.feature-icon { font-size: 18px; opacity: 0.9; }
.login-form-area { flex: 1; padding: 50px 44px; background: #fff; display: flex; flex-direction: column; justify-content: center; }
.form-header { margin-bottom: 32px; }
.form-header h2 { font-size: 26px; font-weight: 700; color: #1a1a1a; margin: 0 0 8px; }
.form-header p { font-size: 14px; color: #909399; margin: 0; }
.captcha-row { display: flex; gap: 12px; }
.captcha-input { flex: 1; }
.captcha-img { width: 120px; height: 40px; border-radius: 8px; background: #f5f7fa; cursor: pointer; display: flex; align-items: center; justify-content: center; border: 1px dashed #dcdfe6; flex-shrink: 0; overflow: hidden; }
.captcha-img:hover { border-color: #67c23a; }
.captcha-img img { width: 100%; height: 100%; object-fit: cover; border-radius: 8px; }
.form-footer { text-align: center; font-size: 14px; color: #909399; margin-top: 8px; }
.form-footer .link { color: #67c23a; text-decoration: none; font-weight: 500; }
</style>
