<template>
  <el-container class="main-layout">
    <el-aside width="220px" class="main-aside">
      <Sidebar />
    </el-aside>
    <el-container>
      <el-header class="main-header">
        <Navbar />
      </el-header>
      <el-main class="main-body">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
</script>

<style scoped>
.main-layout { height: 100vh; }
.main-aside { background: #1a1a2e; overflow: hidden; }
.main-header { height: 56px !important; padding: 0 20px; display: flex; align-items: center; background: #fff; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08); }
.main-body { background: #f0f2f5; min-height: calc(100vh - 56px); }
</style>
