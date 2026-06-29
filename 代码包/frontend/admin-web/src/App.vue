<template>
  <router-view />
</template>

<script setup>
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
  font-family: 'Helvetica Neue', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* Element Plus 主题色覆写 — 绿色主题 */
:root {
  --el-color-primary: #67c23a;
  --el-color-primary-light-3: #85ce61;
  --el-color-primary-light-5: #a4db8a;
  --el-color-primary-light-7: #c2e7b0;
  --el-color-primary-light-8: #d3efc5;
  --el-color-primary-light-9: #e5f5da;
  --el-color-primary-dark-2: #529b2e;
}

/* 页面通用背景 */
.page-container {
  padding: 20px;
  background: #f0f2f5;
  min-height: 100%;
}

/* 卡片通用样式 */
.page-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

/* 页面标题 */
.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 20px;
}
</style>
