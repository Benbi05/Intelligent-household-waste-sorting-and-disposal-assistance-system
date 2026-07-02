<template>
  <div class="apply-wrapper">
    <div class="apply-card">
      <h2>商家入驻申请</h2>
      <p class="subtitle">填写店铺信息和证明文件，提交后等待管理员审核</p>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" size="large" style="margin-top:28px">
        <el-divider content-position="left">账号信息</el-divider>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="用于登录系统" maxlength="32" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="至少6位" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="password2">
          <el-input v-model="form.password2" type="password" placeholder="再次输入密码" show-password />
        </el-form-item>

        <el-divider content-position="left">店铺信息</el-divider>
        <el-form-item label="店铺名称" prop="storeName">
          <el-input v-model="form.storeName" placeholder="如：好邻居便利店" maxlength="64" />
        </el-form-item>
        <el-form-item label="联系人" prop="contactName">
          <el-input v-model="form.contactName" placeholder="如：王大姐" maxlength="32" />
        </el-form-item>
        <el-form-item label="手机号" prop="contactPhone">
          <el-input v-model="form.contactPhone" placeholder="11位手机号" maxlength="11" />
        </el-form-item>
        <el-form-item label="所在社区" prop="area">
          <el-select v-model="form.area" placeholder="请选择所在社区" style="width:100%">
            <el-option v-for="c in communities" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="店铺地址">
          <el-input v-model="form.storeAddress" placeholder="详细地址（选填）" maxlength="128" />
        </el-form-item>

        <el-divider content-position="left">证明文件</el-divider>
        <el-form-item label="营业执照" prop="businessLicense">
          <div class="upload-box">
            <el-upload
              :auto-upload="true"
              :show-file-list="false"
              :before-upload="beforeUpload"
              :http-request="(opt) => handleUpload(opt, 'businessLicense')"
              accept="image/*"
            >
              <img v-if="form.businessLicense" :src="form.businessLicense" class="preview-img" />
              <div v-else class="upload-placeholder">
                <el-icon :size="28"><Plus /></el-icon>
                <span>点击上传</span>
              </div>
            </el-upload>
            <span class="upload-tip">支持 JPG/PNG，不超过 5MB</span>
          </div>
        </el-form-item>
        <el-form-item label="身份证" prop="idCard">
          <div class="upload-box">
            <el-upload
              :auto-upload="true"
              :show-file-list="false"
              :before-upload="beforeUpload"
              :http-request="(opt) => handleUpload(opt, 'idCard')"
              accept="image/*"
            >
              <img v-if="form.idCard" :src="form.idCard" class="preview-img" />
              <div v-else class="upload-placeholder">
                <el-icon :size="28"><Plus /></el-icon>
                <span>点击上传</span>
              </div>
            </el-upload>
            <span class="upload-tip">上传身份证正面照片</span>
          </div>
        </el-form-item>

        <el-form-item style="margin-top:24px">
          <el-button type="primary" :loading="loading" @click="handleSubmit" style="width:100%" size="large">提 交 申 请</el-button>
        </el-form-item>
      </el-form>

      <div class="form-footer">
        已有账号？<router-link to="/login" class="link">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { apply } from '@/api/auth'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const communities = ['虎溪花园','学府悦园','康居西城','龙湖U城','金科廊桥水乡','富力城','恒大未来城','融创文旅城']

const form = reactive({
  username: '', password: '', password2: '',
  storeName: '', contactName: '', contactPhone: '', area: '', storeAddress: '',
  businessLicense: '', idCard: '',
})

const rules = {
  username: [{ required: true, message: '请设置登录用户名', trigger: 'blur' }, { min: 3, message: '至少3位', trigger: 'blur' }],
  password: [{ required: true, message: '请设置密码', trigger: 'blur' }, { min: 6, message: '至少6位', trigger: 'blur' }],
  password2: [{ required: true, message: '请确认密码', trigger: 'blur' }, { validator: (r,v,cb) => cb(v !== form.password ? new Error('两次密码不一致') : undefined), trigger: 'blur' }],
  storeName: [{ required: true, message: '请输入店铺名称', trigger: 'blur' }],
  contactName: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  contactPhone: [{ required: true, message: '请输入手机号', trigger: 'blur' }, { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' }],
  area: [{ required: true, message: '请选择所在社区', trigger: 'change' }],
  businessLicense: [{ required: true, message: '请上传营业执照', trigger: 'change' }],
  idCard: [{ required: true, message: '请上传身份证', trigger: 'change' }],
}

function beforeUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isImage) { ElMessage.error('只能上传图片文件'); return false }
  if (!isLt5M) { ElMessage.error('图片不能超过 5MB'); return false }
  return true
}

function handleUpload(opt, field) {
  const reader = new FileReader()
  reader.onload = (e) => {
    form[field] = e.target.result
    ElMessage.success('上传成功')
    formRef.value?.validateField(field)
  }
  reader.readAsDataURL(opt.file)
}

async function handleSubmit() {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }
  loading.value = true
  try {
    await apply({
      username: form.username, password: form.password,
      storeName: form.storeName, contactName: form.contactName, contactPhone: form.contactPhone,
      area: form.area, storeAddress: form.storeAddress,
      businessLicense: form.businessLicense, idCard: form.idCard,
    })
    ElMessage.success('申请已提交，请等待管理员审核（1-2个工作日）')
    router.push('/login')
  } catch { /* handled */ }
  loading.value = false
}
</script>

<style scoped>
.apply-wrapper { width: 100%; min-height: 100vh; display: flex; align-items: flex-start; justify-content: center; background: linear-gradient(135deg, #f0f2f5 0%, #e8eaed 100%); padding: 40px 20px; }
.apply-card { width: 640px; padding: 36px 40px; background: #fff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.08); }
.apply-card h2 { font-size: 24px; font-weight: 700; color: #303133; margin: 0; }
.subtitle { font-size: 14px; color: #909399; margin: 8px 0 0; }
.upload-box { display: flex; flex-direction: column; gap: 6px; }
.preview-img { width: 200px; height: 120px; object-fit: cover; border-radius: 8px; border: 1px solid #ebeef5; }
.upload-placeholder { width: 200px; height: 120px; border: 2px dashed #dcdfe6; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #c0c4cc; cursor: pointer; transition: border-color .2s; }
.upload-placeholder:hover { border-color: #67c23a; color: #67c23a; }
.upload-placeholder span { font-size: 12px; margin-top: 4px; }
.upload-tip { font-size: 12px; color: #c0c4cc; }
.form-footer { text-align: center; font-size: 14px; color: #909399; margin-top: 12px; }
.form-footer .link { color: #67c23a; text-decoration: none; font-weight: 500; }
</style>
