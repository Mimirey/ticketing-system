<script setup lang="ts">
import Tag from 'primevue/tag'
import { STATUS_SEVERITY } from '@/constant/ticket'

defineProps<{ status: string }>()
</script>

<template>
  <Tag :value="status" :severity="STATUS_SEVERITY[status] ?? 'secondary'" />
</template>