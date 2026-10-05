<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import dayjs from 'dayjs'
import Button from 'primevue/button'
import Message from 'primevue/message'
import StatCard from '@/components/StatCard.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import PriorityBadge from '@/components/PriorityBadge.vue'
import { fetchTickets, type Ticket } from '@/api/ticket'
import { getErrorMessage } from '@/api/client'
import { STATUS_OPTIONS, STATUS_SEVERITY } from '@/constant/ticket'
import { useAuthStore } from '@/stores/auth'

// SESUAIKAN dengan nilai di app/models/enums.py
const WAITING = ['Open', 'Assigned']
const IN_PROGRESS = ['In Progress', 'QA']
const DONE = ['Done']

const BAR_COLOR: Record<string, string> = {
  secondary: 'bg-slate-400',
  info: 'bg-sky-500',
  warn: 'bg-amber-500',
  contrast: 'bg-slate-700',
  success: 'bg-emerald-500',
  danger: 'bg-red-500',
}

const router = useRouter()
const auth = useAuthStore()

const tickets = ref<Ticket[]>([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''

  try {
    // Batas backend 100 per halaman, jadi angka dihitung dari 100 tiket terbaru
    tickets.value = await fetchTickets({
      page: 1,
      page_size: 100,
      sort_by: 'created_at',
      order: 'desc',
    })
  } catch (e) {
    error.value = getErrorMessage(e, 'Gagal memuat data dashboard')
  } finally {
    loading.value = false
  }
}

onMounted(load)

const countOf = (statuses: string[]) =>
  tickets.value.filter((t) => statuses.includes(t.status)).length

const stats = computed(() => ({
  total: tickets.value.length,
  waiting: countOf(WAITING),
  inProgress: countOf(IN_PROGRESS),
  done: countOf(DONE),
}))

const overdue = computed(() =>
  tickets.value.filter(
    (t) =>
      !DONE.includes(t.status) &&
      t.due_date &&
      dayjs(t.due_date).isBefore(dayjs()),
  ),
)

const distribution = computed(() =>
  STATUS_OPTIONS.map((status) => {
    const count = tickets.value.filter((t) => t.status === status).length

    const percent = tickets.value.length
      ? Math.round((count / tickets.value.length) * 100)
      : 0

    return {
      status,
      count,
      percent,
      color: BAR_COLOR[STATUS_SEVERITY[status] ?? 'secondary'],
    }
  }),
)

const recent = computed(() => tickets.value.slice(0, 5))

const firstName = computed(() => auth.user?.name?.split(' ')[0] ?? '')

const subtitle = computed(() =>
  auth.user?.role === 'STAFF_IT'
    ? 'Ringkasan ticket yang ditugaskan kepadamu'
    : 'Ringkasan ticket yang kamu laporkan',
)

const formatDate = (iso: string) => dayjs(iso).format('DD MMM YYYY')
</script>

<template>
  <div class="mx-auto max-w-7xl p-6">
    <!-- Header -->
    <div class="mb-6 flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-xl font-bold text-slate-800">
          Halo, {{ firstName }}
        </h1>

        <p class="mt-1 text-sm text-slate-500">
          {{ subtitle }}
        </p>
      </div>

      <Button
        v-if="auth.can('ticket:create')"
        label="Buat Ticket"
        icon="pi pi-plus"
        size="small"
        @click="router.push({ name: 'ticket-create' })"
      />    
    </div>

    <!-- Error -->
    <Message
      v-if="error"
      severity="error"
      size="small"
      :closable="false"
      class="mb-6"
    >
      <div class="flex items-center gap-3">
        <span>{{ error }}</span>

        <Button
          label="Coba lagi"
          size="small"
          variant="text"
          @click="load"
        />
      </div>
    </Message>

    <!-- Kartu ringkasan -->
    <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard
        label="Total Ticket"
        :value="stats.total"
        icon="pi pi-ticket"
        :loading="loading"
      />

      <StatCard
        label="Menunggu"
        :value="stats.waiting"
        icon="pi pi-clock"
        :loading="loading"
      />

      <StatCard
        label="Dikerjakan"
        :value="stats.inProgress"
        icon="pi pi-spinner"
        :loading="loading"
      />

      <StatCard
        label="Selesai"
        :value="stats.done"
        icon="pi pi-check-circle"
        :loading="loading"
      />
    </div>

    <!-- Ticket overdue -->
    <Message
      v-if="overdue.length"
      severity="warn"
      size="small"
      :closable="false"
      class="mb-6"
    >
      {{ overdue.length }} ticket melewati tenggat dan belum selesai.
    </Message>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-5">
      <!-- Sebaran status -->
      <section
        class="rounded-xl border border-slate-200 bg-white p-5 lg:col-span-2"
      >
        <h2 class="mb-4 text-sm font-semibold text-slate-800">
          Sebaran Status
        </h2>

        <p
          v-if="!loading && !stats.total"
          class="py-6 text-center text-sm text-slate-500"
        >
          Belum ada data.
        </p>

        <ul v-else class="flex flex-col gap-4">
          <li
            v-for="item in distribution"
            :key="item.status"
          >
            <div
              class="mb-1 flex items-center justify-between text-sm"
            >
              <span class="text-slate-600">
                {{ item.status }}
              </span>

              <span class="font-medium text-slate-800">
                {{ item.count }}
              </span>
            </div>

            <div
              class="h-2 overflow-hidden rounded-full bg-slate-100"
            >
              <div
                class="h-full rounded-full transition-all duration-500"
                :class="item.color"
                :style="{ width: `${item.percent}%` }"
              ></div>
            </div>
          </li>
        </ul>
      </section>

      <!-- Ticket terbaru -->
      <section
        class="rounded-xl border border-slate-200 bg-white p-5 lg:col-span-3"
      >
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-sm font-semibold text-slate-800">
            Ticket Terbaru
          </h2>

          <RouterLink
            :to="{ name: 'tickets' }"
            class="text-sm font-medium text-(--p-primary-color) hover:underline"
          >
            Lihat semua
          </RouterLink>
        </div>

        <!-- Loading -->
        <div
          v-if="loading"
          class="flex flex-col gap-3"
        >
          <div
            v-for="n in 4"
            :key="n"
            class="h-12 animate-pulse rounded-lg bg-slate-100"
          ></div>
        </div>

        <!-- Empty state -->
        <div
          v-else-if="!recent.length"
          class="flex flex-col items-center gap-3 py-8 text-center"
        >
          <i class="pi pi-inbox text-3xl text-slate-300"></i>

          <p class="text-sm text-slate-500">
            Kamu belum membuat ticket.
          </p>

          <Button
            label="Buat Ticket Pertama"
            size="small"
            variant="outlined"
            @click="router.push({ name: 'ticket-create' })"
          />
        </div>

        <ul
          v-else
          class="divide-y divide-slate-100"
        >
          <li
            v-for="t in recent"
            :key="t.id"
            class="flex items-center gap-3 py-3"
          >
            <div class="min-w-0 flex-1">
              <p
                class="truncate text-sm font-medium text-slate-800"
              >
                {{ t.title }}
              </p>

              <p class="text-xs text-slate-500">
                {{ t.ticket_number }} · {{ formatDate(t.created_at) }}
              </p>
            </div>

            <PriorityBadge
              :priority="t.priority"
              class="hidden sm:inline-flex"
            />

            <StatusBadge :status="t.status" />
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>