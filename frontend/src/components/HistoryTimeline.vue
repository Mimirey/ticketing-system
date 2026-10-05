<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import dayjs from 'dayjs'
import Message from 'primevue/message'
import { fetchHistory, type HistoryEntry } from '@/api/history'
import { getErrorMessage } from '@/api/client'
import { ROLE_LABELS, type Role } from '@/constant/permissions'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  ticketId: number
  ticketNumber: string
}>()

const auth = useAuthStore()

const entries = ref<HistoryEntry[]>([])
const loading = ref(true)
const error = ref('')

type Seg = {
  t: string
  b: boolean
}

const n = (t: string): Seg => ({
  t,
  b: false,
})

const b = (t: string): Seg => ({
  t,
  b: true,
})

const EMPTY = new Set([
  '',
  '-',
  '—',
  'none',
  'null',
  'belum ada',
])

const clean = (v: string | null) => {
  const t = (v ?? '').trim()

  return EMPTY.has(t.toLowerCase()) ? null : t
}

function describe(
  e: HistoryEntry,
  isFirst: boolean,
  ticketNumber: string,
): { icon: string; segments: Seg[] } {
  const field = e.field.trim().toLowerCase()
  const oldV = clean(e.oldValue)
  const newV = clean(e.newValue) ?? '-'
  const isStatus = field.includes('status')

  // Tiket dibuat: status tanpa nilai lama,
  // atau entri paling awal yang berisi Open
  if (isStatus && (!oldV || (isFirst && newV === 'Open'))) {
    return {
      icon: 'pi pi-plus-circle',
      segments: [
        n('membuat ticket '),
        b(ticketNumber),
      ],
    }
  }

  if (isStatus) {
    return {
      icon: 'pi pi-sync',
      segments: [
        n('mengubah status dari '),
        b(oldV!),
        n(' ke '),
        b(newV),
      ],
    }
  }

  if (field === 'pic') {
    if (!oldV) {
      return {
        icon: 'pi pi-user-plus',
        segments: [
          n('menugaskan ticket ke '),
          b(newV),
        ],
      }
    }

    return {
      icon: 'pi pi-user-edit',
      segments: [
        n('mengganti PIC dari '),
        b(oldV),
        n(' ke '),
        b(newV),
      ],
    }
  }

  if (field === 'priority') {
    return {
      icon: 'pi pi-flag',
      segments: [
        n('mengubah prioritas dari '),
        b(oldV ?? '-'),
        n(' ke '),
        b(newV),
      ],
    }
  }

  return {
    icon: 'pi pi-pencil',
    segments: [
      n(`mengubah ${e.field} dari `),
      b(oldV ?? '-'),
      n(' ke '),
      b(newV),
    ],
  }
}

function actorOf(e: HistoryEntry) {
  if (e.actorId && e.actorId === auth.user?.id) {
    return 'Kamu'
  }

  if (e.actorName) {
    return e.actorName
  }

  return e.actorId
    ? `User #${e.actorId}`
    : 'Sistem'
}

const roleOf = (e: HistoryEntry) =>
  e.actorRole
    ? (ROLE_LABELS[e.actorRole as Role] ?? e.actorRole)
    : null

const rows = computed(() =>
  [...entries.value]
    .sort(
      (a, c) =>
        dayjs(a.changedAt).valueOf() -
        dayjs(c.changedAt).valueOf(),
    )
    .map((e, i) => ({
      ...e,
      actor: actorOf(e),
      role: roleOf(e),
      view: describe(
        e,
        i === 0,
        props.ticketNumber,
      ),
    })),
)

onMounted(async () => {
  try {
    entries.value = await fetchHistory(props.ticketId)
  } catch (e) {
    error.value = getErrorMessage(
      e,
      'Gagal memuat riwayat',
    )
  } finally {
    loading.value = false
  }
})

const formatTime = (iso: string) =>
  dayjs(iso).format('DD MMM YYYY, HH:mm')
</script>

<template>
  <div>
    <Message v-if="error" severity="error" size="small" :closable="false">{{ error }}</Message>

    <div v-else-if="loading" class="flex flex-col gap-3">
      <div v-for="n in 3" :key="n" class="h-12 animate-pulse rounded-lg bg-slate-100"></div>
    </div>

    <p v-else-if="!rows.length" class="py-6 text-center text-sm text-slate-500">
      Belum ada riwayat.
    </p>

    <ol v-else class="relative ml-3 border-l border-slate-200">
      <li v-for="r in rows" :key="r.id" class="mb-6 ml-6 last:mb-0">
        <span
          class="absolute -left-3.5 flex h-7 w-7 items-center justify-center rounded-full bg-(--p-primary-50) text-(--p-primary-color) ring-4 ring-white"
        >
          <i :class="r.view.icon" class="text-xs"></i>
        </span>

        <p class="text-sm text-slate-700">
          <span class="font-semibold text-slate-800">{{ r.actor }}</span>
          <span v-if="r.role" class="text-xs text-slate-500"> ({{ r.role }})</span>
          <template v-for="(s, i) in r.view.segments" :key="i">
            <span v-if="s.b" class="font-medium text-slate-800">{{ s.t }}</span>
            <template v-else>{{ ' ' + s.t }}</template>
          </template>
        </p>
        <p class="mt-0.5 text-xs text-slate-500">{{ formatTime(r.changedAt) }}</p>
      </li>
    </ol>
  </div>
</template>