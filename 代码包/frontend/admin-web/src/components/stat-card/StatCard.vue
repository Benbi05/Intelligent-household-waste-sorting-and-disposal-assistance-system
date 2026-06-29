<template>
  <el-card class="stat-card" shadow="never" :style="{ borderTop: '3px solid ' + color }">
    <div class="stat-card-body">
      <div class="stat-info">
        <div class="stat-label">{{ label }}</div>
        <div class="stat-value">{{ value }}</div>
        <div v-if="trend" class="stat-trend">
          <el-icon :color="trend > 0 ? '#67c23a' : '#f56c6c'">
            <CaretTop v-if="trend > 0" /><CaretBottom v-else />
          </el-icon>
          <span>{{ Math.abs(trend) }}%</span>
          <span class="trend-desc">较上月</span>
        </div>
      </div>
      <div class="stat-icon" :style="{ background: color + '1a', color: color }">
        <slot name="icon">
          <el-icon :size="24"><DataLine /></el-icon>
        </slot>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { CaretTop, CaretBottom, DataLine } from '@element-plus/icons-vue'

defineProps({
  label: { type: String, default: '' },
  value: { type: [String, Number], default: 0 },
  trend: { type: Number, default: 0 },
  color: { type: String, default: '#67c23a' },
})
</script>

<style scoped>
.stat-card {
  border-radius: 8px;
  cursor: default;
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
}

.stat-card-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.2;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  font-size: 13px;
  color: #606266;
}

.trend-desc {
  color: #c0c4cc;
  margin-left: 4px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
</style>
