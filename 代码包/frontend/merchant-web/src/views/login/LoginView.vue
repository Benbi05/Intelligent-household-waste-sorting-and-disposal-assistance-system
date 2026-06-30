<template>
  <div class="login-wrapper">
    <div class="login-bg">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
    </div>

    <div class="login-card">
      <!-- 左侧品牌区 -->
      <div class="login-brand">
        <div class="brand-overlay"></div>
        <div class="brand-content">
          <div class="brand-icon">
            <svg viewBox="0 0 80 80" fill="none">
              <circle cx="40" cy="40" r="36" stroke="rgba(255,255,255,0.3)" stroke-width="2" stroke-dasharray="8 4"/>
              <path d="M20 40C20 29 29 20 40 20C48.5 20 55.7 25.2 58.5 32" stroke="white" stroke-width="3" stroke-linecap="round" fill="none"/>
              <path d="M60 40C60 51 51 60 40 60C31.5 60 24.3 54.8 21.5 48" stroke="white" stroke-width="3" stroke-linecap="round" fill="none"/>
              <polygon points="54,28 60,32 58,24" fill="white"/>
              <polygon points="26,52 20,48 22,56" fill="white"/>
              <path d="M40 55C40 55 30 45 32 35C34 28 42 25 42 25C42 25 38 30 40 38C42 46 52 42 52 42C52 42 44 55 40 55Z" fill="rgba(255,255,255,0.9)"/>
            </svg>
          </div>
          <h1 class="brand-title">智能垃圾分类监管<br/>与积分运营系统</h1>
          <p class="brand-subtitle">Intelligent Waste Sorting Supervision<br/>&amp; Points Operation System</p>
          <div class="brand-features">
            <div class="feature-item"><span class="feature-icon">📦</span><span>商品管理</span></div>
            <div class="feature-item"><span class="feature-icon">📋</span><span>订单核销</span></div>
            <div class="feature-item"><span class="feature-icon">📊</span><span>经营报表</span></div>
            <div class="feature-item"><span class="feature-icon">👥</span><span>子账号</span></div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="login-form-area">
        <div class="form-header">
          <h2>商家登录</h2>
          <p>欢迎回来，请登录您的商家账号</p>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" class="login-form" @keyup.enter="handleLogin">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" :prefix-icon="User" size="large" />
          </el-form-item>

          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="请输入密码" :prefix-icon="Lock" size="large" show-password />
          </el-form-item>

          <el-form-item prop="captchaCode">
            <div class="captcha-row">
              <el-input v-model="form.captchaCode" placeholder="请输入图形验证码" :prefix-icon="Key" size="large" maxlength="4" class="captcha-input" />
              <div class="captcha-img" @click="refreshCaptcha" title="点击刷新">
                <img v-if="captchaImage" :src="captchaImage" alt="验证码" />
                <span v-else>加载中...</span>
              </div>
            </div>
          </el-form-item>

          <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleLogin">登 录</el-button>
        </el-form>

        <div class="form-footer">
          还没有账号？<router-link to="/apply" class="apply-link">申请入驻</router-link>
        </div>
      </div>
    </div>
    <div class="login-footer">&copy; 2026 智能垃圾分类监管与积分运营系统 v1.0</div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, Lock, Key } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store'
import request from '@/api/request'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const captchaImage = ref('')
const captchaToken = ref('')

const form = reactive({ username: '', password: '', captchaCode: '' })
const rules = {
  username: [{ required: true, message: '请输入商家用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captchaCode: [{ required: true, message: '请输入图形验证码', trigger: 'blur' }],
}

onMounted(refreshCaptcha)

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
    ElMessage.success('登录成功！欢迎 ' + userStore.storeName)
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch { refreshCaptcha() }
  loading.value = false
}
</script>

<style scoped>
.login-wrapper { position: relative; width: 100%; height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #0a1628 0%, #1a3a4a 40%, #0d5e3a 100%); overflow: hidden; }
.login-bg { position: absolute; inset: 0; pointer-events: none; z-index: 0; }
.bg-shape { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.15; }
.shape-1 { width: 500px; height: 500px; background: #67c23a; top: -150px; right: -100px; animation: float1 8s ease-in-out infinite; }
.shape-2 { width: 400px; height: 400px; background: #409eff; bottom: -120px; left: -80px; animation: float2 10s ease-in-out infinite; }
.shape-3 { width: 300px; height: 300px; background: #e6a23c; top: 40%; left: 45%; animation: float3 12s ease-in-out infinite; }
@keyframes float1 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(-30px,20px) scale(1.05); } }
@keyframes float2 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(30px,-20px) scale(1.08); } }
@keyframes float3 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(-15px,-15px) scale(1.06); } }

.login-card { position: relative; z-index: 1; display: flex; width: 960px; min-height: 540px; border-radius: 20px; box-shadow: 0 25px 80px rgba(0,0,0,0.35); overflow: hidden; }
.login-brand { width: 420px; flex-shrink: 0; background: linear-gradient(160deg, #1a6b3c 0%, #0d5e3a 30%, #0b4a2e 70%, #083820 100%); display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative; }
.brand-overlay { position: absolute; inset: 0; background: radial-gradient(circle at 20% 80%, rgba(103,194,58,0.2) 0%, transparent 50%), radial-gradient(circle at 70% 20%, rgba(64,158,255,0.15) 0%, transparent 50%); }
.brand-content { position: relative; z-index: 2; text-align: center; padding: 40px 30px; color: #fff; }
.brand-icon { margin-bottom: 24px; }
.brand-icon svg { width: 90px; height: 90px; }
.brand-title { font-size: 22px; font-weight: 700; line-height: 1.5; margin: 0 0 10px; letter-spacing: 2px; text-shadow: 0 2px 8px rgba(0,0,0,0.3); }
.brand-subtitle { font-size: 10px; font-weight: 400; opacity: 0.7; letter-spacing: 1.5px; margin: 0 0 32px; text-transform: uppercase; }
.brand-features { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 10px; }
.feature-item { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: rgba(255,255,255,0.1); border-radius: 10px; font-size: 13px; font-weight: 500; backdrop-filter: blur(4px); transition: background 0.3s; }
.feature-item:hover { background: rgba(255,255,255,0.18); }
.feature-icon { font-size: 18px; opacity: 0.9; }

.login-form-area { flex: 1; padding: 50px 44px; background: #fff; display: flex; flex-direction: column; justify-content: center; }
.form-header { margin-bottom: 32px; }
.form-header h2 { font-size: 26px; font-weight: 700; color: #1a1a1a; margin: 0 0 8px; }
.form-header p { font-size: 14px; color: #909399; margin: 0; }
.login-form :deep(.el-form-item) { margin-bottom: 22px; }
.captcha-row { display: flex; gap: 12px; }
.captcha-input { flex: 1; }
.captcha-img { width: 120px; height: 40px; border-radius: 8px; background: #f5f7fa; cursor: pointer; display: flex; align-items: center; justify-content: center; border: 1px dashed #dcdfe6; flex-shrink: 0; overflow: hidden; }
.captcha-img:hover { border-color: #67c23a; }
.captcha-img img { width: 100%; height: 100%; object-fit: cover; border-radius: 8px; }

.login-btn { width: 100%; height: 46px; font-size: 16px; font-weight: 600; letter-spacing: 4px; --el-button-bg-color: #67c23a; --el-button-border-color: #67c23a; --el-button-hover-bg-color: #85ce61; --el-button-hover-border-color: #85ce61; }

.form-footer { text-align: center; font-size: 14px; color: #909399; margin-top: 16px; }
.form-footer .apply-link { color: #67c23a; text-decoration: none; font-weight: 500; margin-left: 4px; }

.login-footer { position: absolute; bottom: 20px; z-index: 1; font-size: 12px; color: rgba(255,255,255,0.35); text-align: center; width: 100%; }
</style>
