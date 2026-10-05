<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import 'dayjs/locale/id'
import relativeTime from 'dayjs/plugin/relativeTime'
import Badge from 'primevue/badge'
import Button from 'primevue/button'
import Message from 'primevue/message'
import Popover from 'primevue/popover'
import {
  fetchNotifications,
  fetchUnreadCount,
  markNotificationRead,
  type AppNotification,
} from '@/api/notification'
import { getErrorMessage } from '@/api/client'

dayjs.extend(relativeTime)
dayjs.locale('id')

const POLL_MS = 30_000

const router = useRouter()

const popover = ref<InstanceType<typeof Popover> | null>(null)
const unread = ref(0)
const items = ref<AppNotification[]>([])
const loading = ref(false)
const error = ref('')

let timer: ReturnType<typeof setInterval> | undefined

async function refreshCount() {
  try {
    unread.value = await fetchUnreadCount()
  } catch {
    // gagal saat polling tidak perlu mengganggu pengguna
  }
}

async function loadList() {
  loading.value = true
  error.value = ''
  try {
    items.value = await fetchNotifications()
  } catch (e) {
    error.value = getErrorMessage(e, 'Gagal memuat notifikasi')
  } finally {
    loading.value = false
  }
}

function startPolling() {
  stopPolling()
  refreshCount()
  timer = setInterval(refreshCount, POLL_MS)
}

function stopPolling() {
  if (timer) clearInterval(timer)
  timer = undefined
}

function onVisibility() {
  if (document.hidden) stopPolling()
  else startPolling()
}

onMounted(() => {
  startPolling()
  document.addEventListener('visibilitychange', onVisibility)
})

onBeforeUnmount(() => {
  stopPolling()
  document.removeEventListener('visibilitychange', onVisibility)
})

function toggle(event: Event) {
  popover.value?.toggle(event)
}

function onShow() {
  loadList()
  refreshCount()
}

async function markRead(n: AppNotification) {
  if (n.isRead) return
  n.isRead = true // langsung berubah di layar
  unread.value = Math.max(0, unread.value - 1)
  try {
    await markNotificationRead(n.id)
  } catch {
    n.isRead = false
    refreshCount()
  }
}

async function open(n: AppNotification) {
  await markRead(n)
  popover.value?.hide()
  if (n.ticketId) router.push({ name: 'ticket-detail', params: { id: n.ticketId } })
}

const hasUnread = computed(() => items.value.some((n) => !n.isRead))

async function markAllRead() {
  const pending = items.value.filter((n) => !n.isRead)
  await Promise.allSettled(pending.map(markRead))
}

const badgeText = computed(() => (unread.value > 99 ? '99+' : String(unread.value)))
const fromNow = (iso: string) => dayjs(iso).fromNow()
</script>

<template>
  <div class="relative">
    <Button
      icon="pi pi-bell"
      severity="secondary"
      variant="text"
      rounded
      aria-label="Notifikasi"
      aria-haspopup="true"
      @click="toggle"
    />
    <span v-if="unread > 0" class="pointer-events-none absolute top-0 right-0">
      <Badge :value="badgeText" severity="danger" size="small" />
    </span>

    <Popover ref="popover" @show="onShow">
      <div class="w-80 max-w-[85vw]">
        <div class="mb-2 flex items-center justify-between">
          <h2 class="text-sm font-semibold text-slate-800">Notifikasi</h2>
          <Button
            v-if="hasUnread"
            label="Tandai semua dibaca"
            size="small"
            variant="text"
            @click="markAllRead"
          />
        </div>

        <Message v-if="error" severity="error" size="small" :closable="false">
          {{ error }}
        </Message>

        <div v-else-if="loading && !items.length" class="flex flex-col gap-2">
          <div v-for="n in 3" :key="n" class="h-14 animate-pulse rounded-lg bg-slate-100"></div>
        </div>

        <div v-else-if="!items.length" class="flex flex-col items-center gap-2 py-8 text-center">
          <i class="pi pi-bell-slash text-3xl text-slate-300"></i>
          <p class="text-sm text-slate-500">Belum ada notifikasi.</p>
        </div>

        <ul v-else class="-mx-1 flex max-h-96 flex-col overflow-y-auto">
          <li v-for="n in items" :key="n.id">
            <button
              type="button"
              class="flex w-full gap-3 rounded-lg px-2 py-2.5 text-left hover:bg-slate-50"
              @click="open(n)"
            >
              <span
                class="mt-1.5 h-2 w-2 shrink-0 rounded-full"
                :class="n.isRead ? 'bg-transparent' : 'bg-(--p-primary-color)'"
              ></span>
              <span class="min-w-0 flex-1">
                <span
                  class="block text-sm text-slate-800"
                  :class="n.isRead ? 'font-normal' : 'font-semibold'"
                >
                  {{ n.title }}
                </span>
                <span class="mt-0.5 block text-xs text-slate-600">{{ n.message }}</span>
                <span class="mt-1 block text-xs text-slate-400">{{ fromNow(n.createdAt) }}</span>
              </span>
            </button>
          </li>
        </ul>
      </div>
    </Popover>
  </div>
</template>