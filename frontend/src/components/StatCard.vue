<script setup lang="ts">
defineProps<{
  label: string
  value: number | string
  icon: string
  loading?: boolean
}>()
</script>

<template>
  <div class="rounded-xl border border-slate-200 bg-white p-5">
    <div class="flex items-center justify-between gap-3">
      <p class="text-sm text-slate-500">{{ label }}</p>
      <i :class="icon" class="text-base text-slate-400" aria-hidden="true"></i>
    </div>

    <div v-if="loading" class="mt-3 h-8 w-14 animate-pulse rounded bg-slate-100"></div>
    <p v-else class="mt-2 text-3xl font-bold tracking-tight text-slate-800">{{ value }}</p>
  </div>
</template>