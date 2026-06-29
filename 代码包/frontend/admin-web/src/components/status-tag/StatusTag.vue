<template>
  <el-tag :type="tagType" :size="size" :effect="effect">
    {{ label }}
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, default: '' },
  size: { type: String, default: 'default' },
  effect: { type: String, default: 'light' },
})

const statusMap = {
  enable: { type: 'success', label: '启用' },
  disable: { type: 'danger', label: '禁用' },
  active: { type: 'success', label: '正常' },
  inactive: { type: 'info', label: '停用' },
  pending: { type: 'warning', label: '待审核' },
  approved: { type: 'success', label: '已通过' },
  rejected: { type: 'danger', label: '已拒绝' },
}

const tagType = computed(() => statusMap[props.status]?.type || 'info')
const label = computed(() => statusMap[props.status]?.label || props.status)
</script>
