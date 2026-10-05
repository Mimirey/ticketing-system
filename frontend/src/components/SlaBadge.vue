<script setup lang="ts">
import { computed } from 'vue'
import Tag from 'primevue/tag'
import { getDueInfo, type DueState } from '@/utils/due'

const props = defineProps<{ dueDate: string | null; status: string }>()

const SEVERITY: Record<DueState, 'secondary' | 'success' | 'warn' | 'danger'> = {
  none: 'secondary',
  done: 'success',
  overdue: 'danger',
  soon: 'warn',
  ok: 'success',
}

const info = computed(() => getDueInfo(props.dueDate, props.status))
</script>

<template>
  <Tag :value="info.label" :severity="SEVERITY[info.state]" class="text-xs!" />
</template>