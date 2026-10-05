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
import {
  downloadExport,
  EmptyFileError,
  fetchTickets,
  type SortField,
  type Ticket,
} from '@/api/ticket'
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
    error.value =
      e instanceof EmptyFileError
        ? e.message
        : getErrorMessage(e, 'Gagal mengekspor data')
  } finally {
    exporting.value = null
  }
}

const formatDate = (iso: string) => dayjs(iso).format('DD MMM YYYY')
</script>

<template>
  <div class="mx-auto max-w-7xl p-4 sm:p-6">
    <!-- Header -->
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3 sm:mb-6">
      <h1 class="text-xl font-bold text-slate-800">Daftar Ticket</h1>

      <div class="flex flex-wrap gap-2">
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

    <!-- Filter -->
    <div class="mb-4 grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:items-center">
      <IconField class="col-span-2 w-full sm:w-72">
        <InputIcon class="pi pi-search" />
        <InputText
          v-model="searchInput"
          placeholder="Cari nomor, judul, atau modul"
          size="small"
          fluid
        />
      </IconField>

      <Select
        v-model="filters.status"
        :options="STATUS_OPTIONS"
        placeholder="Semua Status"
        show-clear
        size="small"
        class="w-full sm:w-40"
      />
      <Select
        v-model="filters.priority"
        :options="PRIORITY_OPTIONS"
        placeholder="Semua Prioritas"
        show-clear
        size="small"
        class="w-full sm:w-44"
      />
      <Select
        v-model="filters.type"
        :options="TYPE_OPTIONS"
        placeholder="Semua Jenis"
        show-clear
        size="small"
        class="w-full sm:w-40"
      />
      <!-- TODO: filter PIC (khusus PM IT), menunggu endpoint daftar user -->

      <Select
        v-model="filters.sortBy"
        :options="SORT_OPTIONS"
        option-label="label"
        option-value="value"
        size="small"
        class="w-full sm:w-48"
      />
      <Button
        :label="filters.order === 'desc' ? 'Turun' : 'Naik'"
        :icon="filters.order === 'desc' ? 'pi pi-arrow-down' : 'pi pi-arrow-up'"
        severity="secondary"
        variant="outlined"
        size="small"
        class="col-span-2 sm:col-span-1"
        @click="toggleOrder"
      />
    </div>

    <Message v-if="error" severity="error" size="small" :closable="false" class="mb-4">
      {{ error }}
    </Message>

    <!-- MOBILE: tampilan kartu -->
    <div class="md:hidden">
      <div v-if="loading" class="py-10 text-center text-sm text-slate-500">
        <i class="pi pi-spin pi-spinner mr-2" />Memuat...
      </div>

      <p
        v-else-if="!tickets.length"
        class="rounded-xl border border-slate-200 bg-white py-8 text-center text-sm text-slate-500"
      >
        Tidak ada ticket ditemukan
      </p>

      <ul v-else class="space-y-3">
        <li
          v-for="t in tickets"
          :key="t.id"
          class="cursor-pointer rounded-xl border border-slate-200 bg-white p-3.5 active:bg-slate-50"
          @click="router.push({ name: 'ticket-detail', params: { id: t.id } })"
        >
          <!-- Baris atas: nomor + status -->
          <div class="flex items-start justify-between gap-2">
            <span class="break-all text-xs font-medium text-slate-500">
              {{ t.ticket_number }}
            </span>
            <StatusBadge :status="t.status" class="shrink-0" />
          </div>

          <!-- Judul -->
          <h2 class="mt-1.5 text-sm font-semibold leading-snug text-slate-800">
            {{ t.title }}
          </h2>

          <!-- Tipe + prioritas -->
          <div class="mt-2.5 flex flex-wrap items-center gap-2">
            <span class="rounded-md bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
              {{ t.type }}
            </span>
            <PriorityBadge :priority="t.priority" />
          </div>

          <!-- Tanggal -->
          <div class="mt-3 grid grid-cols-2 gap-3 border-t border-slate-100 pt-3 text-xs">
            <div>
              <p class="text-slate-400">Tenggat</p>
              <template v-if="t.due_date">
                <p class="mt-0.5 text-slate-700">{{ formatDate(t.due_date) }}</p>
                <p
                  class="mt-0.5"
                  :class="DUE_TEXT_CLASS[getDueInfo(t.due_date, t.status).state]"
                >
                  {{ getDueInfo(t.due_date, t.status).label }}
                </p>
              </template>
              <p v-else class="mt-0.5 text-slate-400">-</p>
            </div>
            <div>
              <p class="text-slate-400">Dibuat</p>
              <p class="mt-0.5 text-slate-700">{{ formatDate(t.created_at) }}</p>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <!-- DESKTOP: tabel -->
    <div class="hidden overflow-hidden rounded-xl border border-slate-200 bg-white md:block">
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

    <!-- Paginasi -->
    <div class="mt-4 flex items-center justify-between gap-2">
      <span class="text-sm text-slate-500">Halaman {{ filters.page }}</span>
      <div class="flex gap-2">
        <Button
          label="Sebelumnya"
          severity="secondary"
          variant="outlined"
          size="small"
          :disabled="filters.page === 1 || loading"
          @click="filters.page--"
        />
        <Button
          label="Selanjutnya"
          severity="secondary"
          variant="outlined"
          size="small"
          :disabled="!hasNext || loading"
          @click="filters.page++"
        />
      </div>
    </div>
  </div>
</template>