<template>
  <div class="login-wrapper">
    <div class="login-bg">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
    </div>

    <div class="login-card">
      <!-- 左侧品牌区 — 深黄色调 -->
      <div class="login-brand">
        <div class="brand-overlay"></div>
        <div class="brand-content">
          <div class="brand-icon">
            <svg viewBox="0 0 80 80" fill="none">
              <circle cx="40" cy="40" r="36" stroke="rgba(255,255,255,0.3)" stroke-width="2" stroke-dasharray="8 4"/>
              <path d="M40 15 C25 15 15 28 15 40 C15 52 28 65 40 65 C52 65 65 52 65 40" stroke="white" stroke-width="3" stroke-linecap="round" fill="none"/>
              <circle cx="40" cy="40" r="12" fill="rgba(255,255,255,0.3)"/>
              <line x1="40" y1="15" x2="40" y2="28" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <line x1="40" y1="52" x2="40" y2="65" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <line x1="15" y1="40" x2="28" y2="40" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <line x1="52" y1="40" x2="65" y2="40" stroke="white" stroke-width="3" stroke-linecap="round"/>
            </svg>
          </div>
          <h1 class="brand-title">智能垃圾分类<br/>AI 运维管理系统</h1>
          <p class="brand-subtitle">System Monitoring · Model Management · Intelligent Analysis</p>
          <div class="brand-features">
            <div class="feature-item"><span class="feature-icon">🖥</span><span>系统监控</span></div>
            <div class="feature-item"><span class="feature-icon">🤖</span><span>AI 模型</span></div>
            <div class="feature-item"><span class="feature-icon">📊</span><span>消费洞察</span></div>
            <div class="feature-item"><span class="feature-icon">🔧</span><span>运维管理</span></div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="login-form-area">
        <div class="form-header">
          <h2>AI 运维管理</h2>
          <p>系统监控 · 模型管理 · 智能分析</p>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" class="login-form" @keyup.enter="handleLogin">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="请输入运维账号" :prefix-icon="User" size="large" />
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
          <div class="form-options"><el-checkbox v-model="rememberMe">记住我</el-checkbox></div>
          <el-button type="warning" size="large" class="login-btn" :loading="loading" @click="handleLogin">登 录</el-button>
        </el-form>

        <div class="form-footer">AI 智能运维管理平台</div>
      </div>
    </div>
    <div class="login-footer">&copy; 2026 智能垃圾分类 · AI 运维管理系统 v1.0</div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, Lock, Key } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import request from '@/api/request'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const rememberMe = ref(false)
const captchaImage = ref('')
const captchaToken = ref('')

const form = reactive({ username: '', password: '', captchaCode: '' })
const rules = {
  username: [{ required: true, message: '请输入运维账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captchaCode: [{ required: true, message: '请输入图形验证码', trigger: 'blur' }],
}

onMounted(() => {
  const saved = localStorage.getItem('ops_remember_user')
  if (saved) { form.username = saved; rememberMe.value = true }
  refreshCaptcha()
})

async function refreshCaptcha() {
  try {
    const res = await request.get('/common/captcha')
    captchaToken.value = res.data.captchaToken
    captchaImage.value = res.data.captchaImage
    form.captchaCode = ''
  } catch {}
}

async function handleLogin() {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }
  loading.value = true
  try {
    await userStore.login(form.username, form.password, captchaToken.value, form.captchaCode)
    if (rememberMe.value) localStorage.setItem('ops_remember_user', form.username)
    else localStorage.removeItem('ops_remember_user')
    ElMessage.success('登录成功！欢迎 ' + userStore.username)
    router.push(route.query.redirect || '/ops-dashboard')
  } catch { refreshCaptcha() }
  finally { loading.value = false }
}
</script>

<style scoped>
.login-wrapper {
  position: relative; width: 100%; height: 100vh; display: flex;
  align-items: center; justify-content: center;
  background: linear-gradient(135deg, #141000 0%, #221a05 40%, #141000 100%);
  overflow: hidden;
}
.login-bg { position: absolute; inset: 0; pointer-events: none; z-index: 0; }
.bg-shape { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.15; }
.shape-1 { width: 500px; height: 500px; background: #f59e0b; top: -150px; right: -100px; animation: float1 8s ease-in-out infinite; }
.shape-2 { width: 400px; height: 400px; background: #e6a400; bottom: -120px; left: -80px; animation: float2 10s ease-in-out infinite; }
.shape-3 { width: 300px; height: 300px; background: #ffca28; top: 40%; left: 45%; animation: float3 12s ease-in-out infinite; }
@keyframes float1 { 0%,100% { transform: translate(0,0) scale(1) } 50% { transform: translate(-30px,20px) scale(1.05) } }
@keyframes float2 { 0%,100% { transform: translate(0,0) scale(1) } 50% { transform: translate(30px,-20px) scale(1.08) } }
@keyframes float3 { 0%,100% { transform: translate(0,0) scale(1) } 50% { transform: translate(-15px,-15px) scale(1.06) } }

.login-card {
  position: relative; z-index: 1; display: flex; width: 960px; min-height: 540px;
  border-radius: 20px; box-shadow: 0 25px 80px rgba(0,0,0,0.35); overflow: hidden;
}
.login-brand {
  width: 420px; flex-shrink: 0;
  background: linear-gradient(160deg, #d49800 0%, #b07a00 30%, #805a00 70%, #504000 100%);
  display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative;
}
.brand-overlay {
  position: absolute; inset: 0;
  background: radial-gradient(circle at 20% 80%, rgba(245,158,11,0.2) 0%, transparent 50%),
    radial-gradient(circle at 70% 20%, rgba(255,202,40,0.12) 0%, transparent 50%);
}
.brand-content { position: relative; z-index: 2; text-align: center; padding: 40px 30px; color: #fff; }
.brand-icon { margin-bottom: 24px; }
.brand-icon svg { width: 90px; height: 90px; }
.brand-title { font-size: 22px; font-weight: 700; line-height: 1.5; margin: 0 0 10px; letter-spacing: 2px; text-shadow: 0 2px 8px rgba(0,0,0,0.3); }
.brand-subtitle { font-size: 10px; font-weight: 400; opacity: 0.7; letter-spacing: 1.5px; margin: 0 0 32px; text-transform: uppercase; }
.brand-features { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 10px; }
.feature-item { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: rgba(255,255,255,0.1); border-radius: 10px; font-size: 13px; font-weight: 500; transition: background 0.3s; }
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
.captcha-img:hover { border-color: #e6a400; }
.captcha-img img { width: 100%; height: 100%; object-fit: cover; border-radius: 8px; }
.form-options { display: flex; align-items: center; justify-content: space-between; margin-bottom: 22px; }
.login-btn { width: 100%; height: 46px; font-size: 16px; font-weight: 600; letter-spacing: 4px; }
.form-footer { text-align: center; font-size: 12px; color: #c0c4cc; margin-top: 16px; }
.login-footer { position: absolute; bottom: 20px; z-index: 1; font-size: 12px; color: rgba(255,255,255,0.35); text-align: center; width: 100%; }

@media (max-width: 1000px) {
  .login-card { width: 90%; flex-direction: column; min-height: auto; }
  .login-brand { width: 100%; padding: 30px 20px; }
  .brand-title { font-size: 18px; }
  .brand-features { display: none; }
  .login-form-area { padding: 30px 24px; }
}
</style>
