<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ status: string }>()

const DOTS: Record<string, string> = {
  Open: 'bg-slate-400',
  Assigned: 'bg-slate-400',
  'In Progress': 'bg-(--p-primary-color)',
  QA: 'bg-(--p-primary-color)',
  Done: 'bg-emerald-500',
}

const dot = computed(() => DOTS[props.status] ?? 'bg-slate-400')
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-2.5 py-0.5 text-xs font-medium whitespace-nowrap text-slate-700"
  >
    <span class="h-1.5 w-1.5 shrink-0 rounded-full" :class="dot" aria-hidden="true"></span>
    {{ status }}
  </span>
</template>