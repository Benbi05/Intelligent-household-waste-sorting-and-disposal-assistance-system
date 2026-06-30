<template>
  <div class="navbar">
    <div class="navbar-left">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-if="route.meta.title">{{ route.meta.title }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="navbar-right">
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-dropdown">
          <el-avatar :size="32" icon="UserFilled" />
          <span class="username">{{ userStore.storeName || '商家' }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item disabled>
              <div class="user-info-item">
                <span class="label">角色：</span>
                <el-tag size="small" type="success">商家</el-tag>
              </div>
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store'
import { ArrowDown, SwitchButton } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

async function handleCommand(command) {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消',
      })
    } catch { return }
    await userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.navbar { display: flex; align-items: center; justify-content: space-between; width: 100%; }
.navbar-left { display: flex; align-items: center; gap: 12px; }
.navbar-right { display: flex; align-items: center; }
.user-dropdown { display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 8px; border-radius: 6px; transition: background 0.2s; }
.user-dropdown:hover { background: #f5f7fa; }
.username { font-size: 14px; color: #303133; }
.user-info-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #909399; }
</style>
