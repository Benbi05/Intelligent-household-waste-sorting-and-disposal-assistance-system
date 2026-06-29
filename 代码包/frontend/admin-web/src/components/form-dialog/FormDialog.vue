<template>
  <el-dialog
    v-model="visible"
    :title="title"
    :width="width"
    :close-on-click-modal="false"
    @close="onClose"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      :label-width="labelWidth"
      v-loading="loading"
    >
      <slot :formData="formData" />
    </el-form>

    <template #footer>
      <el-button @click="onClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="onConfirm">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '表单' },
  width: { type: String, default: '520px' },
  labelWidth: { type: String, default: '100px' },
  formData: { type: Object, default: () => ({}) },
  rules: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'confirm', 'close'])

const formRef = ref(null)

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

async function onConfirm() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    emit('confirm')
  } catch {
    // validation failed
  }
}

function onClose() {
  formRef.value?.resetFields()
  emit('close')
}
</script>
