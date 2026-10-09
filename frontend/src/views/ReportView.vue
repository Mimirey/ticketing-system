<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import dayjs from 'dayjs'
import Button from 'primevue/button'
import Chart from 'primevue/chart'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import DatePicker from 'primevue/datepicker'
import Message from 'primevue/message'
import MultiSelect from 'primevue/multiselect'
import { fetchTicketReport, type StatusCounts, type TicketReport, type TicketStatus } from '@/api/reports'
import { getErrorMessage } from '@/api/client'

type StaffRow = TicketReport['by_staff'][number]

const STATUS_KEYS: TicketStatus[] = ['OPEN', 'ASSIGNED', 'IN_PROGRESS', 'QA', 'DONE']

const STATUS_META: Record<TicketStatus, { label: string; color: string }> = {
  OPEN: { label: 'Open', color: '#94a3b8' },
  ASSIGNED: { label: 'Assigned', color: '#3b82f6' },
  IN_PROGRESS: { label: 'In Progress', color: '#f59e0b' },
  QA: { label: 'QA', color: '#8b5cf6' },
  DONE: { label: 'Selesai', color: '#10b981' },
}

const today = new Date()
const dateRange = ref<(Date | null)[] | null>([dayjs().startOf('month').toDate(), today])

const report = ref<TicketReport | null>(null)
const loading = ref(true)
const error = ref('')
const selectedIds = ref<number[]>([])
const firstLoad = ref(true)

const hasRange = computed(() => !!dateRange.value?.[0] && !!dateRange.value?.[1])

async function load() {
  const range = dateRange.value
  if (!range?.[0] || !range?.[1]) return

  loading.value = true
  error.value = ''
  try {
    const data = await fetchTicketReport({
      start_date: dayjs(range[0]).format('YYYY-MM-DD'),
      end_date: dayjs(range[1]).format('YYYY-MM-DD'),
    })
    report.value = data

    const ids = data.by_staff.map((s) => s.staff_id)
    if (firstLoad.value) {
      selectedIds.value = ids
      firstLoad.value = false
    } else {
      const kept = selectedIds.value.filter((id) => ids.includes(id))
      selectedIds.value = kept.length ? kept : ids
    }
  } catch (e) {
    error.value = getErrorMessage(e, 'Gagal memuat report')
  } finally {
    loading.value = false
  }
}

onMounted(load)

watch(dateRange, () => {
  if (hasRange.value) load()
})

const staffOptions = computed(() => report.value?.by_staff ?? [])

const selectedStaff = computed(() =>
  staffOptions.value.filter((s) => selectedIds.value.includes(s.staff_id)),
)

function selectAll() {
  selectedIds.value = staffOptions.value.map((s) => s.staff_id)
}

function clearAll() {
  selectedIds.value = []
}

const count = (s: StaffRow, k: TicketStatus) => s.by_status?.[k] ?? 0

const totals = computed<StatusCounts>(() => {
  const t: StatusCounts = { OPEN: 0, ASSIGNED: 0, IN_PROGRESS: 0, QA: 0, DONE: 0 }
  for (const s of selectedStaff.value) {
    for (const k of STATUS_KEYS) t[k] += count(s, k)
  }
  return t
})

const grandTotal = computed(() => selectedStaff.value.reduce((sum, s) => sum + s.total, 0))

const completionRate = computed(() =>
  grandTotal.value ? Math.round((totals.value.DONE / grandTotal.value) * 100) : 0,
)

const stats = computed(() => [
  { key: 'total', label: 'Total Ticket', value: grandTotal.value, tone: 'text-slate-800', hint: '' },
  { key: 'assigned', label: 'Assigned', value: totals.value.ASSIGNED, tone: 'text-blue-600', hint: '' },
  { key: 'progress', label: 'In Progress', value: totals.value.IN_PROGRESS, tone: 'text-amber-600', hint: '' },
  {
    key: 'done',
    label: 'Selesai',
    value: totals.value.DONE,
    tone: 'text-emerald-600',
    hint: `${completionRate.value}% dari total`,
  },
])

const legend = {
  position: 'bottom',
  labels: { usePointStyle: true, boxWidth: 8, padding: 14, font: { size: 11 } },
}

const barData = computed(() => ({
  labels: selectedStaff.value.map((s) => s.staff_name),
  datasets: STATUS_KEYS.map((k) => ({
    label: STATUS_META[k].label,
    backgroundColor: STATUS_META[k].color,
    data: selectedStaff.value.map((s) => count(s, k)),
    maxBarThickness: 36,
  })),
}))

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend },
  scales: {
    x: { stacked: true, grid: { display: false }, ticks: { font: { size: 11 } } },
    y: { stacked: true, beginAtZero: true, ticks: { precision: 0, font: { size: 11 } } },
  },
}

const doughnutData = computed(() => ({
  labels: STATUS_KEYS.map((k) => STATUS_META[k].label),
  datasets: [
    {
      data: STATUS_KEYS.map((k) => totals.value[k]),
      backgroundColor: STATUS_KEYS.map((k) => STATUS_META[k].color),
      borderWidth: 0,
    },
  ],
}))

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '65%',
  plugins: { legend },
}
</script>

<template>
  <div class="mx-auto max-w-6xl px-4 py-5 sm:px-6">
    <h1 class="mb-5 text-xl font-bold text-slate-800">Report</h1>

    <Message v-if="error" severity="error" size="small" :closable="false" class="mb-4">
      <div class="flex items-center gap-3">
        <span>{{ error }}</span>
        <Button label="Coba lagi" size="small" variant="text" @click="load" />
      </div>
    </Message>

    <div class="flex flex-col gap-5">
      <section class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-[1fr_1fr_auto] lg:items-end">
          <div class="flex flex-col gap-1.5">
            <label for="period-filter" class="text-sm font-medium text-slate-800">Periode</label>
            <DatePicker
              v-model="dateRange"
              input-id="period-filter"
              selection-mode="range"
              date-format="dd/mm/yy"
              placeholder="Pilih rentang tanggal"
              :max-date="today"
              :manual-input="false"
              :disabled="loading"
              show-icon
              icon-display="input"
              size="small"
              fluid
            />
          </div>

          <div class="flex flex-col gap-1.5">
            <label for="staff-filter" class="text-sm font-medium text-slate-800">Staff</label>
            <MultiSelect
              v-model="selectedIds"
              input-id="staff-filter"
              :options="staffOptions"
              option-label="staff_name"
              option-value="staff_id"
              placeholder="Pilih staff"
              filter
              :max-selected-labels="2"
              selected-items-label="{0} staff dipilih"
              :disabled="loading || !staffOptions.length"
              size="small"
              fluid
            />
          </div>

          <div class="flex gap-2">
            <Button
              label="Pilih Semua"
              size="small"
              variant="outlined"
              severity="secondary"
              :disabled="loading || !staffOptions.length"
              @click="selectAll"
            />
            <Button
              label="Kosongkan"
              size="small"
              variant="text"
              severity="secondary"
              :disabled="loading || !selectedIds.length"
              @click="clearAll"
            />
          </div>
        </div>

        <p v-if="!hasRange" class="mt-3 text-xs text-slate-500">
          Pilih tanggal mulai dan tanggal akhir untuk memuat report.
        </p>

        <dl
          v-if="report && !loading"
          class="mt-5 grid grid-cols-2 gap-x-6 gap-y-3 border-t border-slate-100 pt-4 lg:grid-cols-4"
        >
          <div v-for="s in stats" :key="s.key">
            <dt class="text-xs text-slate-500">{{ s.label }}</dt>
            <dd class="mt-0.5 text-xl leading-tight font-semibold" :class="s.tone">{{ s.value }}</dd>
            <p v-if="s.hint" class="mt-0.5 text-xs text-slate-500">{{ s.hint }}</p>
          </div>
        </dl>
      </section>

      <div v-if="loading" class="flex flex-col gap-5">
        <div class="h-64 animate-pulse rounded-xl bg-slate-100"></div>
        <div class="h-44 animate-pulse rounded-xl bg-slate-100"></div>
      </div>

      <template v-else-if="report">
        <section
          v-if="!staffOptions.length"
          class="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500"
        >
          Tidak ada data ticket pada periode ini.
        </section>

        <section
          v-else-if="!selectedStaff.length"
          class="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500"
        >
          Pilih minimal satu staff untuk melihat report.
        </section>

        <template v-else>
          <section class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
              <div class="lg:col-span-2">
                <h2 class="mb-3 text-sm font-semibold text-slate-800">Ticket per Staff</h2>
                <div class="h-64">
                  <Chart type="bar" :data="barData" :options="barOptions" class="h-full" />
                </div>
              </div>
              <div class="lg:border-l lg:border-slate-100 lg:pl-6">
                <h2 class="mb-3 text-sm font-semibold text-slate-800">Komposisi Status</h2>
                <div class="h-64">
                  <Chart type="doughnut" :data="doughnutData" :options="doughnutOptions" class="h-full" />
                </div>
              </div>
            </div>
          </section>

          <section class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <div class="border-b border-slate-100 px-5 py-3">
              <h2 class="text-sm font-semibold text-slate-800">Rincian per Staff</h2>
            </div>

            <DataTable
              :value="selectedStaff"
              data-key="staff_id"
              size="small"
              scrollable
              class="text-sm! [&_th]:py-2! [&_th]:text-xs! [&_th]:font-semibold! [&_th]:text-slate-500! [&_td]:py-2!"
            >
              <Column field="staff_name" header="Staff" style="min-width: 10rem">
                <template #body="{ data }">
                  <span class="font-medium whitespace-nowrap text-slate-800">{{ data.staff_name }}</span>
                </template>
              </Column>

              <Column
                v-for="k in STATUS_KEYS"
                :key="k"
                style="min-width: 5.5rem"
                header-class="[&_.p-datatable-column-header-content]:justify-center"
                body-class="text-center"
              >
                <template #header>
                  <span class="inline-flex items-center gap-1.5 whitespace-nowrap">
                    <span
                      class="h-2 w-2 rounded-full"
                      :style="{ backgroundColor: STATUS_META[k].color }"
                    ></span>
                    {{ STATUS_META[k].label }}
                  </span>
                </template>
                <template #body="{ data }">
                  <span :class="count(data, k) ? 'font-medium text-slate-800' : 'text-slate-300'">
                    {{ count(data, k) }}
                  </span>
                </template>
              </Column>

              <Column
                field="total"
                header="Total"
                style="min-width: 5rem"
                header-class="[&_.p-datatable-column-header-content]:justify-center"
                body-class="text-center"
              >
                <template #body="{ data }">
                  <span class="font-semibold text-slate-800">{{ data.total }}</span>
                </template>
              </Column>
            </DataTable>
          </section>
        </template>
      </template>
    </div>
  </div>
</template>