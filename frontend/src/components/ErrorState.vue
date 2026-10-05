<script setup lang="ts">
defineProps<{
  icon: string
  title: string
  description?: string
}>()
</script>

<template>
  <div class="flex flex-col items-center px-4 py-16 text-center" role="alert">
    <div class="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-slate-100">
      <i :class="icon" class="text-2xl text-slate-500"></i>
    </div>
    <h2 class="text-lg font-semibold text-slate-800">{{ title }}</h2>
    <p v-if="description" class="mt-2 max-w-md text-sm text-slate-500">{{ description }}</p>
    <div class="mt-6 flex flex-wrap justify-center gap-2">
      <slot />
    </div>
  </div>
</template>