<template>
  <div class="navbar">
    <div class="navbar-left">
      <el-icon class="collapse-btn" @click="$emit('toggleSidebar')">
        <Fold v-if="!appStore.sidebarCollapsed" />
        <Expand v-else />
      </el-icon>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-if="route.meta.title">{{ route.meta.title }}</el-breadcrumb-item>
      </el-breadcrumb>

      <el-select
        v-if="isAdmin"
        v-model="activeCommunity"
        placeholder="选择社区"
        size="small"
        style="width:150px;margin-left:16px"
        clearable
        @change="onCommunityChange"
      >
        <el-option v-for="c in communities" :key="c.value" :label="c.label" :value="c.value" />
      </el-select>
    </div>

    <div class="navbar-right">
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-dropdown">
          <el-avatar :size="32" icon="UserFilled" />
          <span class="username">{{ userStore.username || '管理员' }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item disabled>
              <div class="user-info-item">
                <span class="label">角色：</span>
                <el-tag size="small" type="success">{{ roleLabel }}</el-tag>
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
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { useAppStore } from '@/store/app'
import { Fold, Expand, ArrowDown, SwitchButton } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

defineEmits(['toggleSidebar'])

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()

const isAdmin = computed(() => userStore.role === 'super_admin')

const roleLabel = computed(() => {
  const map = { super_admin: '物业经理', admin: '城管监管' }
  return map[userStore.role] || userStore.role
})

const communities = [
  { label: '虎溪花园', value: '虎溪' }, { label: '学府悦园', value: '学府' },
  { label: '康居西城', value: '康居' }, { label: '龙湖U城', value: '龙湖' },
  { label: '金科廊桥水乡', value: '金科' }, { label: '富力城', value: '富力' },
  { label: '恒大未来城', value: '恒大' }, { label: '融创文旅城', value: '融创' },
]
const activeCommunity = ref(route.query.community || '')

watch(() => route.query.community, (val) => {
  activeCommunity.value = val || ''
})

function onCommunityChange(val) {
  const q = { ...route.query }
  if (val) q.community = val
  else delete q.community
  router.push({ query: q })
}

async function handleCommand(command) {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消',
      })
    } catch {
      return
    }
    await userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.collapse-btn {
  font-size: 20px;
  color: #606266;
  cursor: pointer;
  transition: color 0.2s;
}

.collapse-btn:hover {
  color: #67c23a;
}

.navbar-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.2s;
}

.user-dropdown:hover {
  background: #f5f7fa;
}

.username {
  font-size: 14px;
  color: #303133;
}

.user-info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #909399;
}
</style>
