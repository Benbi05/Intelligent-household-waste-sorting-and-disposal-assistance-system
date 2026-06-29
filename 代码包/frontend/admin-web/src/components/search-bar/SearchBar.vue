<template>
  <div class="search-bar">
    <el-form :inline="true" :model="form" class="search-form">
      <el-form-item v-if="showKeyword" label="关键词">
        <el-input
          v-model="form.keyword"
          placeholder="请输入搜索关键词"
          clearable
          :style="{ width: keywordWidth }"
          @keyup.enter="onSearch"
          @clear="onSearch"
        />
      </el-form-item>

      <el-form-item v-if="showStatus" label="状态">
        <el-select
          v-model="form.status"
          placeholder="全部"
          clearable
          :style="{ width: statusWidth }"
          @change="onSearch"
          @clear="onSearch"
        >
          <el-option
            v-for="opt in statusOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </el-form-item>

      <slot name="extra" :form="form" />

      <el-form-item>
        <el-button type="primary" @click="onSearch">
          <el-icon><Search /></el-icon>搜索
        </el-button>
        <el-button @click="onReset">
          <el-icon><RefreshRight /></el-icon>重置
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'
import { Search, RefreshRight } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
  showKeyword: { type: Boolean, default: true },
  showStatus: { type: Boolean, default: false },
  keywordWidth: { type: String, default: '220px' },
  statusWidth: { type: String, default: '140px' },
  statusOptions: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue', 'search', 'reset'])

const form = reactive({ ...props.modelValue })

watch(() => props.modelValue, (val) => {
  Object.assign(form, val)
}, { deep: true })

function onSearch() {
  emit('update:modelValue', { ...form })
  emit('search')
}

function onReset() {
  Object.keys(form).forEach((k) => {
    form[k] = ''
  })
  emit('update:modelValue', { ...form })
  emit('reset')
}
</script>

<style scoped>
.search-bar {
  background: #fff;
  padding: 16px 20px 0;
  border-radius: 8px;
  margin-bottom: 16px;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
}

.search-form :deep(.el-form-item) {
  margin-bottom: 16px;
}
</style>
