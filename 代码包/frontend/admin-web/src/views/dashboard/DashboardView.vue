<template>
  <div class="page-container">
    <h2 class="page-title">仪表盘</h2>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <StatCard
          label="居民用户总数"
          :value="stats.userCount"
          :trend="12"
          color="#67c23a"
        >
          <template #icon><el-icon :size="24"><User /></el-icon></template>
        </StatCard>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <StatCard
          label="智能设备数"
          :value="stats.deviceCount"
          :trend="5"
          color="#409eff"
        >
          <template #icon><el-icon :size="24"><Monitor /></el-icon></template>
        </StatCard>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <StatCard
          label="今日回收次数"
          :value="stats.todayDelivery"
          :trend="8"
          color="#e6a23c"
        >
          <template #icon><el-icon :size="24"><Delete /></el-icon></template>
        </StatCard>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <StatCard
          label="积分总发放"
          :value="stats.totalPoints"
          :trend="-3"
          color="#f56c6c"
        >
          <template #icon><el-icon :size="24"><Coin /></el-icon></template>
        </StatCard>
      </el-col>
    </el-row>

    <!-- 快速入口 -->
    <el-row :gutter="20" class="quick-row">
      <el-col :span="12">
        <div class="page-card">
          <h3 class="card-title">快速操作</h3>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/users')">
              <el-icon><User /></el-icon>用户管理
            </el-button>
            <el-button type="success" @click="$router.push('/system/areas')">
              <el-icon><Location /></el-icon>区域管理
            </el-button>
          </div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="page-card">
          <h3 class="card-title">系统信息</h3>
          <el-descriptions :column="1" size="small" border>
            <el-descriptions-item label="系统版本">v1.0.0</el-descriptions-item>
            <el-descriptions-item label="前端框架">Vue 3 + Element Plus</el-descriptions-item>
            <el-descriptions-item label="后端服务">Flask + MySQL + Redis</el-descriptions-item>
            <el-descriptions-item label="AI 服务">YOLOv8 + LLM</el-descriptions-item>
          </el-descriptions>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { User, Monitor, Delete, Coin, Location } from '@element-plus/icons-vue'
import StatCard from '@/components/stat-card/StatCard.vue'

// 静态占位数据（后端 statistics 接口尚未实现）
const stats = reactive({
  userCount: 1256,
  deviceCount: 48,
  todayDelivery: 389,
  totalPoints: 158200,
})
</script>

<style scoped>
.stat-row {
  margin-bottom: 20px;
}

.quick-row {
  margin-top: 0;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.quick-actions {
  display: flex;
  gap: 12px;
}
</style>
