<template>
  <el-container class="main-layout">
    <el-aside :width="sidebarCollapsed ? '64px' : '220px'" class="main-aside">
      <Sidebar :collapsed="sidebarCollapsed" />
    </el-aside>
    <el-container>
      <el-header class="main-header">
        <Navbar @toggle-sidebar="toggleSidebar" />
      </el-header>
      <el-main class="main-body">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '@/store/app'
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'

const appStore = useAppStore()
const sidebarCollapsed = computed(() => appStore.sidebarCollapsed)

function toggleSidebar() {
  appStore.toggleSidebar()
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.main-aside {
  background: #1a1a2e;
  transition: width 0.3s;
  overflow: hidden;
}

.main-header {
  height: 56px !important;
  padding: 0 20px;
  display: flex;
  align-items: center;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.main-body {
  background: #f0f2f5;
  min-height: calc(100vh - 56px);
}
</style>
