<script setup lang="ts">
defineProps<{
  label: string
  value: number | string
  icon: string
  loading?: boolean
}>()
</script>

<template>
  <div class="flex items-center gap-4 rounded-xl border border-slate-200 bg-white p-5">
    <div
      class="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-(--p-primary-50) text-(--p-primary-color)"
    >
      <i :class="icon" class="text-lg"></i>
    </div>
    <div>
      <p class="text-sm text-slate-500">{{ label }}</p>
      <div v-if="loading" class="mt-1 h-7 w-12 animate-pulse rounded bg-slate-100"></div>
      <p v-else class="text-2xl font-bold text-slate-800">{{ value }}</p>
    </div>
  </div>
</template>