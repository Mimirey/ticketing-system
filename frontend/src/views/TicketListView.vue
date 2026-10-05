<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import dayjs from 'dayjs'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Select from 'primevue/select'
import Button from 'primevue/button'
import Message from 'primevue/message'
import StatusBadge from '@/components/StatusBadge.vue'
import PriorityBadge from '@/components/PriorityBadge.vue'
import { downloadExport, fetchTickets, type SortField, type Ticket } from '@/api/ticket'
import { getErrorMessage } from '@/api/client'
import { PRIORITY_OPTIONS, SORT_OPTIONS, STATUS_OPTIONS, TYPE_OPTIONS } from '@/constant/ticket'
import { useAuthStore } from '@/stores/auth'
import { DUE_TEXT_CLASS, getDueInfo } from '@/utils/due'

const PAGE_SIZE = 10

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const isPM = computed(() => auth.user?.role === 'PM_IT')

const str = (v: unknown) => (typeof v === 'string' && v ? v : null)
const q = route.query

const filters = reactive({
  search: str(q.search) ?? '',
  status: str(q.status),
  priority: str(q.priority),
  type: str(q.type),
  sortBy: (str(q.sort_by) as SortField | null) ?? 'created_at',
  order: q.order === 'asc' ? ('asc' as const) : ('desc' as const),
  page: Number(q.page) > 0 ? Number(q.page) : 1,
})

const searchInput = ref(filters.search)
const tickets = ref<Ticket[]>([])
const loading = ref(false)
const error = ref('')
const exporting = ref<'excel' | 'pdf' | null>(null)

const hasNext = computed(() => tickets.value.length === PAGE_SIZE)

async function load() {
  loading.value = true
  error.value = ''
  try {
    tickets.value = await fetchTickets({
      search: filters.search || undefined,
      status: filters.status ?? undefined,
      priority: filters.priority ?? undefined,
      type: filters.type ?? undefined,
      sort_by: filters.sortBy,
      order: filters.order,
      page: filters.page,
      page_size: PAGE_SIZE,
    })
  } catch (e) {
    error.value = getErrorMessage(e, 'Gagal memuat tiket')
  } finally {
    loading.value = false
  }
}

function syncUrl() {
  router.replace({
    query: {
      search: filters.search || undefined,
      status: filters.status ?? undefined,
      priority: filters.priority ?? undefined,
      type: filters.type ?? undefined,
      sort_by: filters.sortBy !== 'created_at' ? filters.sortBy : undefined,
      order: filters.order !== 'desc' ? filters.order : undefined,
      page: filters.page > 1 ? String(filters.page) : undefined,
    },
  })
}

function apply() {
  syncUrl()
  load()
}

// Pencarian ditunda 400 ms supaya tidak memanggil API di setiap ketukan
let searchTimer: ReturnType<typeof setTimeout> | undefined
watch(searchInput, (v) => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => (filters.search = v.trim()), 400)
})

// Perubahan filter apa pun kembali ke halaman 1
watch(
  () => [filters.search, filters.status, filters.priority, filters.type, filters.sortBy, filters.order],
  () => (filters.page === 1 ? apply() : (filters.page = 1)),
)
watch(() => filters.page, apply)

onMounted(load)

function toggleOrder() {
  filters.order = filters.order === 'desc' ? 'asc' : 'desc'
}

async function onExport(kind: 'excel' | 'pdf') {
  exporting.value = kind
  try {
    await downloadExport(kind)
  } catch (e) {
    error.value = getErrorMessage(e, 'Gagal mengekspor data')
  } finally {
    exporting.value = null
  }
}

const formatDate = (iso: string) => dayjs(iso).format('DD MMM YYYY')
</script>

<template>
  <div class="mx-auto max-w-7xl p-6">
    <div class="mb-6 flex flex-wrap items-center justify-between gap-3">
      <h1 class="text-xl font-bold text-slate-800">Daftar Ticket</h1>

      <div class="flex gap-2">
        <template v-if="isPM">
          <Button
            label="Export Excel"
            icon="pi pi-file-excel"
            severity="secondary"
            variant="outlined"
            size="small"
            :loading="exporting === 'excel'"
            @click="onExport('excel')"
          />
          <Button
            label="Export PDF"
            icon="pi pi-file-pdf"
            severity="secondary"
            variant="outlined"
            size="small"
            :loading="exporting === 'pdf'"
            @click="onExport('pdf')"
          />
        </template>
            <Button
              v-if="auth.can('ticket:create')"
              label="Buat Ticket"
              icon="pi pi-plus"
              size="small"
              @click="router.push({ name: 'ticket-create' })"
            />       
      </div>
    </div>

    <div class="mb-4 flex flex-wrap items-center gap-2">
      <IconField class="w-full sm:w-72">
        <InputIcon class="pi pi-search" />
        <InputText
          v-model="searchInput"
          placeholder="Cari nomor, judul, atau modul"
          size="small"
          fluid
        />
      </IconField>

      <Select v-model="filters.status" :options="STATUS_OPTIONS" placeholder="Semua Status" show-clear size="small" class="w-40" />
      <Select v-model="filters.priority" :options="PRIORITY_OPTIONS" placeholder="Semua Prioritas" show-clear size="small" class="w-44" />
      <Select v-model="filters.type" :options="TYPE_OPTIONS" placeholder="Semua Jenis" show-clear size="small" class="w-40" />
      <!-- TODO: filter PIC (khusus PM IT), menunggu endpoint daftar user -->

      <Select
        v-model="filters.sortBy"
        :options="SORT_OPTIONS"
        option-label="label"
        option-value="value"
        size="small"
        class="w-48"
      />
      <Button
        :label="filters.order === 'desc' ? 'Turun' : 'Naik'"
        :icon="filters.order === 'desc' ? 'pi pi-arrow-down' : 'pi pi-arrow-up'"
        severity="secondary"
        variant="outlined"
        size="small"
        @click="toggleOrder"
      />
    </div>

    <Message v-if="error" severity="error" size="small" :closable="false" class="mb-4">
      {{ error }}
    </Message>

    <div class="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <DataTable
        :value="tickets"
        :loading="loading"
        size="small"
        data-key="id"
        row-hover
        class="text-sm! [&_th]:py-2.5! [&_th]:text-xs! [&_th]:font-semibold! [&_th]:text-slate-500! [&_td]:py-2!"
        :pt="{ bodyRow: { class: 'cursor-pointer' } }"
        @row-click="(e) => router.push({ name: 'ticket-detail', params: { id: e.data.id } })"
      >
        <Column field="ticket_number" header="Nomor" />
        <Column field="title" header="Judul" />
        <Column field="type" header="Tipe" />
        <Column header="Status">
          <template #body="{ data }"><StatusBadge :status="data.status" /></template>
        </Column>
        <Column header="Prioritas">
          <template #body="{ data }"><PriorityBadge :priority="data.priority" /></template>
        </Column>

        <Column header="Tenggat">
          <template #body="{ data }">
            <div v-if="data.due_date" class="leading-tight">
              <p>{{ formatDate(data.due_date) }}</p>
              <p
                class="text-xs"
                :class="DUE_TEXT_CLASS[getDueInfo(data.due_date, data.status).state]"
              >
                {{ getDueInfo(data.due_date, data.status).label }}
              </p>
            </div>
            <span v-else class="text-slate-400">-</span>
          </template>
        </Column>

        <Column header="Dibuat">
          <template #body="{ data }">{{ formatDate(data.created_at) }}</template>
        </Column>
        <template #empty>
          <p class="py-6 text-center text-sm text-slate-500">Tidak ada ticket ditemukan</p>
        </template>
      </DataTable>
    </div>

    <div class="mt-4 flex items-center justify-between">
      <span class="text-sm text-slate-500">Halaman {{ filters.page }}</span>
      <div class="flex gap-2">
        <Button label="Sebelumnya" severity="secondary" variant="outlined" size="small" :disabled="filters.page === 1 || loading" @click="filters.page--" />
        <Button label="Selanjutnya" severity="secondary" variant="outlined" size="small" :disabled="!hasNext || loading" @click="filters.page++" />
      </div>
    </div>
  </div>
</template>