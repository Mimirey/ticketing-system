<script setup lang="ts">
import Tag from 'primevue/tag'
import { PRIORITY_SEVERITY } from '@/constant/ticket'

defineProps<{ priority: string }>()
</script>

<template>
  <Tag :value="priority" :severity="PRIORITY_SEVERITY[priority] ?? 'secondary'" />
</template>