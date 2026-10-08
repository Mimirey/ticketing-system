<script setup lang="ts">
import { computed } from 'vue'
import { PASSWORD_RULES } from '@/utils/password'

const props = defineProps<{
  password: string
}>()

const results = computed(() =>
  PASSWORD_RULES.map((rule) => ({
    label: rule.label,
    ok: !!props.password && rule.test(props.password),
  })),
)
</script>

<template>
  <ul class="flex flex-col gap-1" aria-label="Syarat password">
    <li
      v-for="r in results"
      :key="r.label"
      class="flex items-center gap-2 text-xs transition-colors"
      :class="r.ok ? 'text-emerald-600' : 'text-slate-500'"
    >
      <i :class="r.ok ? 'pi pi-check-circle' : 'pi pi-circle'" class="text-[11px]"></i>
      {{ r.label }}
    </li>
  </ul>
</template>