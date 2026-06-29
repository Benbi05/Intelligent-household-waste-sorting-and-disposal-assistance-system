<template>
  <div class="page-container">
    <div class="page-card detail-page">
      <div class="detail-header">
        <el-button @click="$router.back()" :icon="ArrowLeft">返回</el-button>
        <h2 class="page-title" style="margin: 0">用户详情</h2>
      </div>

      <div v-if="user" class="detail-body">
        <el-descriptions :column="2" border size="default">
          <el-descriptions-item label="用户ID">{{ user.userId }}</el-descriptions-item>
          <el-descriptions-item label="昵称">{{ user.nickName }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ user.phone }}</el-descriptions-item>
          <el-descriptions-item label="积分余额">{{ user.pointBalance }}</el-descriptions-item>
          <el-descriptions-item label="累计投递次数">{{ user.totalDeliveryTimes }}</el-descriptions-item>
          <el-descriptions-item label="分类正确率">{{ (user.correctRate * 100).toFixed(1) }}%</el-descriptions-item>
        </el-descriptions>
      </div>

      <div v-else v-loading="loading" class="empty-state">
        <span v-if="!loading">用户不存在</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getUserDetail } from '@/api/user'

const route = useRoute()
const user = ref(null)
const loading = ref(true)

onMounted(async () => {
  const userId = route.params.userId
  try {
    const res = await getUserDetail(userId)
    user.value = res.data
  } catch {
    user.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-page {
  max-width: 900px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.detail-body {
  margin-top: 0;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  color: #909399;
}
</style>
