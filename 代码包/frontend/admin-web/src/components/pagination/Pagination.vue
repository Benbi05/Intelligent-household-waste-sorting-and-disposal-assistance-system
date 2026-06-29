<template>
  <div class="pagination-wrap" v-if="total > 0">
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="currentSize"
      :page-sizes="pageSizes"
      :total="total"
      :layout="layout"
      :background="true"
      @size-change="onChange"
      @current-change="onChange"
    />
    <span class="total-text">共 {{ total }} 条</span>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  total: { type: Number, default: 0 },
  page: { type: Number, default: 1 },
  size: { type: Number, default: 10 },
  pageSizes: { type: Array, default: () => [10, 20, 50, 100] },
  layout: { type: String, default: 'sizes, prev, pager, next, jumper' },
})

const emit = defineEmits(['update:page', 'update:size', 'change'])

const currentPage = ref(props.page)
const currentSize = ref(props.size)

watch(() => props.page, (v) => { currentPage.value = v })
watch(() => props.size, (v) => { currentSize.value = v })

function onChange() {
  emit('update:page', currentPage.value)
  emit('update:size', currentSize.value)
  emit('change', { page: currentPage.value, size: currentSize.value })
}
</script>

<style scoped>
.pagination-wrap {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 16px 0 0;
  gap: 12px;
}

.total-text {
  font-size: 13px;
  color: #909399;
  white-space: nowrap;
}
</style>
