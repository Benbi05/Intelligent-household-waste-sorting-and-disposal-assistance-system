<template>
  <div class="data-table">
    <el-table
      :data="data"
      :height="height"
      empty-text="暂无数据"
      border
      stripe
      @selection-change="onSelectionChange"
      @sort-change="onSortChange"
      :default-sort="defaultSort"
    >
      <el-table-column
        v-if="showSelection"
        type="selection"
        width="48"
        align="center"
      />
      <slot />
      <el-table-column
        v-if="$slots.actions || actionWidth"
        label="操作"
        :width="actionWidth || 180"
        align="center"
        fixed="right"
      >
        <template #default="{ row, $index }">
          <slot name="actions" :row="row" :index="$index" />
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
defineProps({
  data: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  height: { type: [String, Number], default: undefined },
  showSelection: { type: Boolean, default: false },
  actionWidth: { type: [String, Number], default: undefined },
  defaultSort: { type: Object, default: undefined },
})

const emit = defineEmits(['selection-change', 'sort-change'])

function onSelectionChange(selection) {
  emit('selection-change', selection)
}

function onSortChange(sort) {
  emit('sort-change', sort)
}
</script>

<style scoped>
.data-table {
  width: 100%;
}

:deep(.el-table) {
  border-radius: 4px;
  font-size: 14px;
}
:deep(.el-table__body-wrapper) {
  min-height: 200px;
}
:deep(.el-table__row) {
  height: 48px;
}

:deep(.el-table th.el-table__cell) {
  background: #f5f7fa;
  color: #606266;
  font-weight: 600;
  height: 48px;
}

:deep(.el-table .el-table__row:hover > td.el-table__cell) {
  background: #f0f9eb;
}

:deep(.el-table__empty-text) {
  color: #c0c4cc;
  font-size: 14px;
}
:deep(.el-table__row) {
  height: 52px !important;
}
:deep(.el-tag) {
  transition: none !important;
}
</style>
