<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title" style="margin-bottom: 0">积分规则 · {{ version }}</h2>
      <div class="header-actions">
        <el-button @click="$router.push('/rules/history')">
          <el-icon><Clock /></el-icon>历史版本
        </el-button>
        <el-button type="primary" @click="openPublishDialog">
          <el-icon><Upload /></el-icon>发布新版本
        </el-button>
      </div>
    </div>

    <div class="page-card" v-loading="loading">
      <DataTable :data="ruleList">
        <el-table-column prop="categoryId" label="分类ID" width="100" align="center" />
        <el-table-column prop="categoryName" label="分类名称" min-width="130" />
        <el-table-column prop="parentTypeName" label="父类" width="110" align="center" />
        <el-table-column prop="rewardPoint" label="奖励积分" width="110" align="center">
          <template #default="{ row }">
            <el-tag type="success" effect="plain">{{ row.rewardPoint }} 分</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="penaltyPoint" label="违规扣分" width="110" align="center">
          <template #default="{ row }">
            <el-tag type="danger" effect="plain">{{ row.penaltyPoint }} 分</el-tag>
          </template>
        </el-table-column>
      </DataTable>
    </div>

    <!-- 发布新版本弹窗 -->
    <el-dialog v-model="publishVisible" title="发布新规则版本" width="800px" :close-on-click-modal="false" destroy-on-close>
      <div class="publish-hint">
        当前版本 <el-tag size="small">{{ version }}</el-tag>，修改下表后发布新版本
      </div>
      <el-table :data="editList" border stripe max-height="480" style="margin-top:12px">
        <el-table-column prop="categoryName" label="分类名称" min-width="130" />
        <el-table-column prop="parentTypeName" label="父类" width="110" align="center" />
        <el-table-column label="奖励积分" width="130" align="center">
          <template #default="{ row }">
            <el-input-number v-model="row.rewardPoint" :min="0" :max="999" size="small" controls-position="right" />
          </template>
        </el-table-column>
        <el-table-column label="违规扣分" width="130" align="center">
          <template #default="{ row }">
            <el-input-number v-model="row.penaltyPoint" :min="0" :max="999" size="small" controls-position="right" />
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="publishVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handlePublish">确认发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Clock, Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getCurrentRules, publishRules } from '@/api/point'
import DataTable from '@/components/table/DataTable.vue'

const loading = ref(false)
const version = ref('v1.0')
const ruleList = ref([])
const submitting = ref(false)
const publishVisible = ref(false)
const editList = ref([])

async function fetchRules() {
  loading.value = true
  try {
    const res = await getCurrentRules()
    version.value = res.data.version || 'v1.0'
    ruleList.value = res.data.ruleList || []
  } catch { /* handled */ } finally { loading.value = false }
}

function openPublishDialog() {
  editList.value = ruleList.value.map(r => ({ ...r }))
  publishVisible.value = true
}

async function handlePublish() {
  submitting.value = true
  try {
    const res = await publishRules(editList.value.map(r => ({
      categoryId: r.categoryId, rewardPoint: r.rewardPoint, penaltyPoint: r.penaltyPoint,
    })))
    ElMessage.success('规则发布成功')
    version.value = res.data.newVersion
    publishVisible.value = false
    fetchRules()
  } catch { /* handled */ } finally { submitting.value = false }
}

onMounted(fetchRules)
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.header-actions { display: flex; gap: 10px; }
.publish-hint { font-size: 13px; color: #909399; }
</style>
