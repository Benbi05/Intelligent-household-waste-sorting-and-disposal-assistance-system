<template>
  <div class="sidebar">
    <div class="sidebar-logo">
      <svg viewBox="0 0 40 40" fill="none" class="logo-icon">
        <circle cx="20" cy="20" r="18" stroke="rgba(103,194,58,0.4)" stroke-width="1.5" stroke-dasharray="6 3"/>
        <path d="M12 20C12 15 17 12 20 14C23 12 28 15 28 20C28 25 23 28 20 26C17 28 12 25 12 20Z" fill="rgba(103,194,58,0.9)"/>
      </svg>
      <span v-show="!collapsed" class="logo-title">垃圾分类管理</span>
    </div>

    <el-menu
      :default-active="activeMenu"
      :collapse="collapsed"
      background-color="#1a1a2e"
      text-color="rgba(255,255,255,0.65)"
      active-text-color="#67c23a"
      router
      class="sidebar-menu"
    >
      <!-- ========== 运维端（精简） ========== -->
      <template v-if="isOps">
        <el-menu-item index="/ops-dashboard">
          <el-icon><MonitorIcon /></el-icon>
          <template #title>系统监控</template>
        </el-menu-item>
        <el-menu-item index="/ops-models">
          <el-icon><Cpu /></el-icon>
          <template #title>AI模型管理</template>
        </el-menu-item>
        <el-menu-item index="/ops-insights">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>消费洞察</template>
        </el-menu-item>
      </template>

      <!-- ========== 城管 + 物业经理 ========== -->
      <template v-if="!isOps">
      <el-menu-item index="/dashboard">
        <el-icon><DataLine /></el-icon>
        <template #title>仪表盘</template>
      </el-menu-item>

      <!-- 8个社区（仅城管可见） -->
      <template v-if="!isAdmin">
        <el-menu-item index="/dashboard?community=虎溪"><el-icon><Location /></el-icon><template #title>虎溪花园</template></el-menu-item>
        <el-menu-item index="/dashboard?community=学府"><el-icon><Location /></el-icon><template #title>学府悦园</template></el-menu-item>
        <el-menu-item index="/dashboard?community=康居"><el-icon><Location /></el-icon><template #title>康居西城</template></el-menu-item>
        <el-menu-item index="/dashboard?community=龙湖"><el-icon><Location /></el-icon><template #title>龙湖U城</template></el-menu-item>
        <el-menu-item index="/dashboard?community=金科"><el-icon><Location /></el-icon><template #title>金科廊桥水乡</template></el-menu-item>
        <el-menu-item index="/dashboard?community=富力"><el-icon><Location /></el-icon><template #title>富力城</template></el-menu-item>
        <el-menu-item index="/dashboard?community=恒大"><el-icon><Location /></el-icon><template #title>恒大未来城</template></el-menu-item>
        <el-menu-item index="/dashboard?community=融创"><el-icon><Location /></el-icon><template #title>融创文旅城</template></el-menu-item>
      </template>

      <el-menu-item index="/users" v-if="isAdmin">
        <el-icon><User /></el-icon>
        <template #title>用户管理</template>
      </el-menu-item>

      <el-menu-item index="/devices" v-if="isAdmin">
        <el-icon><Monitor /></el-icon>
        <template #title>设备管理</template>
      </el-menu-item>

      <el-menu-item index="/merchants" v-if="isAdmin">
        <el-icon><Shop /></el-icon>
        <template #title>商家审核</template>
      </el-menu-item>

      <el-sub-menu index="rules-group" v-if="isAdmin">
        <template #title>
          <el-icon><Coin /></el-icon>
          <span>积分规则</span>
        </template>
        <el-menu-item index="/rules">当前规则</el-menu-item>
        <el-menu-item index="/rules/history">历史版本</el-menu-item>
        <el-menu-item index="/categories">品类管理</el-menu-item>
      </el-sub-menu>

      <el-menu-item index="/statistics">
        <el-icon><TrendCharts /></el-icon>
        <template #title>数据统计</template>
      </el-menu-item>

      </template>  <!-- end v-if="!isOps" -->
    </el-menu>

    <div class="sidebar-footer" v-show="!collapsed">
      <span class="version-text">v1.0</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { DataLine, User, Monitor, Shop, Coin, TrendCharts, Location, Cpu, DataAnalysis, Monitor as MonitorIcon } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

defineProps({
  collapsed: { type: Boolean, default: false },
})

const route = useRoute()
const userStore = useUserStore()
const isAdmin = computed(() => userStore.role === 'super_admin')
const isOps = computed(() => userStore.role === 'ops_admin')
const activeMenu = computed(() => '/' + route.path.split('/').slice(1, 3).join('/'))
</script>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  gap: 10px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}

.logo-title {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  letter-spacing: 1px;
}

.sidebar-menu {
  flex: 1;
  border-right: none !important;
}

.sidebar-menu .el-menu-item {
  margin: 4px 8px;
  border-radius: 6px;
  height: 44px;
  line-height: 44px;
  font-size: 14px;
}

.sidebar-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.08) !important;
}

.sidebar-menu .el-menu-item.is-active {
  background: rgba(103, 194, 58, 0.15) !important;
}

.sidebar-menu :deep(.el-sub-menu__title) {
  margin: 4px 8px;
  border-radius: 6px;
  height: 44px;
  line-height: 44px;
  font-size: 14px;
}

.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background: rgba(255, 255, 255, 0.08) !important;
}

.sidebar-footer {
  padding: 12px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.version-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.25);
}
</style>
