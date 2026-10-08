<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import dayjs from 'dayjs'
import Button from 'primevue/button'
import Message from 'primevue/message'
import Select from 'primevue/select'
import { fetchActivityLogs, type ActivityLog } from '@/api/activity'
import { getErrorMessage } from '@/api/client'
import { ACTION_OPTIONS, actionMeta } from '@/constant/activity'

const PAGE_SIZE = 20

const action = ref<string | null>(null)
const page = ref(1)
const raw = ref<ActivityLog[]>([])
const loading = ref(true)
const error = ref('')

const clientMode = computed(() => raw.value.length > PAGE_SIZE)

const filtered = computed(() =>
  clientMode.value && action.value
    ? raw.value.filter((l) => l.action === action.value)
    : raw.value,
)

const pageRows = computed(() =>
  clientMode.value
    ? filtered.value.slice((page.value - 1) * PAGE_SIZE, page.value * PAGE_SIZE)
    : raw.value,
)

const hasNext = computed(() =>
  clientMode.value ? page.value * PAGE_SIZE < filtered.value.length : raw.value.length === PAGE_SIZE,
)

const rows = computed(() =>
  pageRows.value.map((log) => ({
    ...log,
    meta: actionMeta(log.action),
    showUser: !!log.userName && !log.description.includes(log.userName),
  })),
)

async function load() {
  loading.value = true
  error.value = ''
  try {
    raw.value = await fetchActivityLogs({
      page: page.value,
      page_size: PAGE_SIZE,
      action: action.value ?? undefined,
    })
  } catch (e) {
    error.value = getErrorMessage(e, 'Gagal memuat activity log')
  } finally {
    loading.value = false
  }
}

function changeAction(value: string | null) {
  action.value = value
  page.value = 1
  load()
}

function goTo(target: number) {
  page.value = target
  if (!clientMode.value) load()
}

onMounted(load)

const formatTime = (iso: string) => dayjs(iso).format('DD MMM YYYY, HH:mm:ss')
</script>

<template>
  <div class="mx-auto max-w-5xl px-6 py-6">
    <div class="mb-6 flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-xl font-bold text-slate-800">Activity Log</h1>
        <p class="mt-1 text-sm text-slate-500">Riwayat aktivitas pengguna di sistem</p>
      </div>

      <div class="flex items-center gap-2">
        <Select
          :model-value="action"
          :options="ACTION_OPTIONS"
          option-label="label"
          option-value="value"
          placeholder="Semua Aksi"
          show-clear
          size="small"
          class="w-44"
          @update:model-value="changeAction"
        />
        <Button
          icon="pi pi-refresh"
          severity="secondary"
          variant="outlined"
          size="small"
          aria-label="Muat ulang"
          :loading="loading"
          @click="load"
        />
      </div>
    </div>

    <Message v-if="error" severity="error" size="small" :closable="false" class="mb-4">
      <div class="flex items-center gap-3">
        <span>{{ error }}</span>
        <Button label="Coba lagi" size="small" variant="text" @click="load" />
      </div>
    </Message>

    <div class="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <div v-if="loading" class="flex flex-col gap-px">
        <div v-for="n in 6" :key="n" class="h-14 animate-pulse bg-slate-50"></div>
      </div>

      <div
        v-else-if="!rows.length"
        class="flex flex-col items-center gap-2 py-12 text-center"
      >
        <i class="pi pi-history text-3xl text-slate-300"></i>
        <p class="text-sm text-slate-500">Belum ada aktivitas.</p>
      </div>

      <ul v-else class="divide-y divide-slate-100">
        <li
          v-for="log in rows"
          :key="log.id"
          class="flex flex-col gap-2 px-4 py-3 hover:bg-slate-50/60 sm:flex-row sm:items-center sm:gap-4"
        >
          <div class="shrink-0 sm:w-44">
            <span
              class="inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium whitespace-nowrap ring-1 ring-inset"
              :class="log.meta.badge"
            >
              <i :class="log.meta.icon" class="text-[11px]" aria-hidden="true"></i>
              {{ log.meta.label }}
            </span>
          </div>

          <p class="min-w-0 flex-1 text-sm text-slate-700">{{ log.description }}</p>

          <div class="shrink-0 text-xs text-slate-500 tabular-nums sm:text-right">
            <p v-if="log.showUser" class="font-medium text-slate-700">{{ log.userName }}</p>
            <p>{{ formatTime(log.createdAt) }}</p>
          </div>
        </li>
      </ul>
    </div>

    <div class="mt-4 flex items-center justify-between">
      <span class="text-sm text-slate-500">Halaman {{ page }}</span>
      <div class="flex gap-2">
        <Button
          label="Sebelumnya"
          severity="secondary"
          variant="outlined"
          size="small"
          :disabled="page === 1 || loading"
          @click="goTo(page - 1)"
        />
        <Button
          label="Selanjutnya"
          severity="secondary"
          variant="outlined"
          size="small"
          :disabled="!hasNext || loading"
          @click="goTo(page + 1)"
        />
      </div>
    </div>
  </div>
</template>