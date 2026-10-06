<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ priority: string }>()

const LEVELS: Record<string, number> = {
  Low: 1,
  Medium: 2,
  High: 3,
  Critical: 4,
}

const BARS: Record<string, string> = {
  Low: 'bg-slate-400',
  Medium: 'bg-slate-500',
  High: 'bg-amber-500',
  Critical: 'bg-red-500',
}

const TEXTS: Record<string, string> = {
  Low: 'text-slate-600',
  Medium: 'text-slate-700',
  High: 'text-amber-700',
  Critical: 'text-red-700',
}

const HEIGHTS = ['h-1.5', 'h-2', 'h-2.5', 'h-3']

const level = computed(() => LEVELS[props.priority] ?? 1)
const bar = computed(() => BARS[props.priority] ?? 'bg-slate-400')
const text = computed(() => TEXTS[props.priority] ?? 'text-slate-600')
</script>

<template>
  <span class="inline-flex items-center gap-2 text-xs font-medium whitespace-nowrap" :class="text">
    <span class="flex items-end gap-0.5" aria-hidden="true">
      <span
        v-for="n in 4"
        :key="n"
        class="w-0.5 rounded-sm"
        :class="[HEIGHTS[n - 1], n <= level ? bar : 'bg-slate-200']"
      ></span>
    </span>
    {{ priority }}
  </span>
</template>