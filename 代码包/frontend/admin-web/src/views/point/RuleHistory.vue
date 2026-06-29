<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title" style="margin-bottom: 0">规则历史版本</h2>
      <el-button @click="$router.push('/rules')">
        <el-icon><ArrowLeft /></el-icon>返回当前规则
      </el-button>
    </div>

    <div class="page-card" v-loading="loading">
      <el-timeline v-if="historyList.length > 0">
        <el-timeline-item
          v-for="(item, idx) in historyList"
          :key="item.version"
          :timestamp="'版本 ' + item.version"
          :color="idx === 0 ? '#67c23a' : '#909399'"
          :icon="idx === 0 ? 'Check' : 'MoreFilled'"
          size="large"
        >
          <el-collapse>
            <el-collapse-item :title="'共 ' + item.ruleList.length + ' 条规则'">
              <el-table :data="item.ruleList" border stripe size="small">
                <el-table-column prop="categoryName" label="分类" min-width="130" />
                <el-table-column prop="parentTypeName" label="父类" width="110" align="center" />
                <el-table-column prop="rewardPoint" label="奖励积分" width="90" align="center" />
                <el-table-column prop="penaltyPoint" label="违规扣分" width="90" align="center" />
              </el-table>
            </el-collapse-item>
          </el-collapse>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无历史版本" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getRulesHistory } from '@/api/point'

const loading = ref(false)
const historyList = ref([])

onMounted(async () => {
  loading.value = true
  try {
    const res = await getRulesHistory()
    historyList.value = res.data.records || []
  } catch { /* handled */ } finally { loading.value = false }
})
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
</style>
