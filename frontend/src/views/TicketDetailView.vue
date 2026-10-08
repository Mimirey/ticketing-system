<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import Button from 'primevue/button'
import DatePicker from 'primevue/datepicker'
import Select from 'primevue/select'
import Message from 'primevue/message'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import StatusBadge from '@/components/StatusBadge.vue'
import PriorityBadge from '@/components/PriorityBadge.vue'
import SlaBadge from '@/components/SlaBadge.vue'
import ErrorState from '@/components/ErrorState.vue'
import AttachmentList from '@/components/AttachmentList.vue'
import CommentSection from '@/components/CommentSection.vue'
import HistoryTimeline from '@/components/HistoryTimeline.vue'
import { getErrorMessage, getErrorStatus } from '@/api/client'
import {
  assignTicket,
  deleteTicket,
  fetchTicket,
  updateTicketDueDate,
  updateTicketPriority,
  updateTicketStatus,
  type Ticket,
} from '@/api/ticket'
import { fetchApplications, fetchCompanies } from '@/api/master'
import { fetchUsers, type UserSummary } from '@/api/users'
import { NEXT_STATUS, PRIORITY_OPTIONS } from '@/constant/ticket'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{ id: number }>()

const router = useRouter()
const toast = useToast()
const confirm = useConfirm()
const auth = useAuthStore()

const ticket = ref<Ticket | null>(null)
const loading = ref(true)
const error = ref('')
const errorStatus = ref<number | null>(null)
const acting = ref(false)

const companyName = ref('-')
const applicationName = ref('-')
const staff = ref<UserSummary[]>([])

const minDate = new Date()
const dueDraft = ref<Date | null>(null)

const isReporter = computed(
  () => !!ticket.value && ticket.value.reporter_id === auth.user?.id,
)

const validId = computed(() => Number.isInteger(props.id) && props.id > 0)
const isPM = computed(() => auth.user?.role === 'PM_IT')
const isDone = computed(() => ticket.value?.status === 'Done')
const canManage = computed(() => auth.can('ticket:assign') && !isDone.value)
const canDelete = computed(() => (isPM.value || isReporter.value) && !isDone.value)

const nextStatuses = computed(() => {
  const t = ticket.value
  if (!t || !auth.can('ticket:handle')) return []
  if (!isPM.value && t.pic_id !== auth.user?.id) return []
  return NEXT_STATUS[t.status] ?? []
})

const showActions = computed(
  () => canManage.value || nextStatuses.value.length > 0 || canDelete.value,
)

const historyKey = computed(() =>
  ticket.value ? `${ticket.value.status}-${ticket.value.pic_id}-${ticket.value.priority}` : '',
)

const dueDirty = computed(() => {
  if (!dueDraft.value) return false
  const current = ticket.value?.due_date
  return !current || !dayjs(dueDraft.value).isSame(dayjs(current), 'minute')
})

watch(
  ticket,
  (t) => {
    dueDraft.value = t?.due_date ? new Date(t.due_date) : null
  },
  { immediate: true },
)

async function load() {
  if (!validId.value) {
    errorStatus.value = 404
    error.value = 'Ticket tidak ditemukan'
    loading.value = false
    return
  }

  error.value = ''
  errorStatus.value = null

  try {
    ticket.value = await fetchTicket(props.id)
  } catch (e) {
    errorStatus.value = getErrorStatus(e) ?? 0
    error.value = getErrorMessage(e, 'Gagal memuat ticket')
  } finally {
    loading.value = false
  }
}

async function retry() {
  loading.value = true
  await load()
}

async function loadNames(t: Ticket) {
  if (t.company?.name && t.application?.name) return
  if (!t.company_id) return

  try {
    const [companies, apps] = await Promise.all([
      fetchCompanies(),
      fetchApplications(t.company_id),
    ])

    companyName.value = companies.find((c) => c.id === t.company_id)?.name ?? '-'
    applicationName.value = apps.find((a) => a.id === t.application_id)?.name ?? '-'
  } catch {
    companyName.value = '-'
    applicationName.value = '-'
  }
}

onMounted(async () => {
  await load()

  if (ticket.value) loadNames(ticket.value)

  if (isPM.value) {
    try {
      staff.value = await fetchUsers('STAFF_IT')
    } catch {
      staff.value = []
    }
  }
})

watch(
  () => props.id,
  async (id, oldId) => {
    if (id === oldId || !Number.isInteger(id) || id <= 0) return

    loading.value = true
    ticket.value = null
    await load()
    if (ticket.value) loadNames(ticket.value)
  },
)

async function run(action: () => Promise<unknown>, success: string) {
  acting.value = true

  try {
    await action()
    toast.add({ severity: 'success', summary: success, life: 3000 })
    await load()
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Gagal',
      detail: getErrorMessage(e),
      life: 5000,
    })
  } finally {
    acting.value = false
  }
}

const onAssign = (picId: number) =>
  run(() => assignTicket(props.id, picId), 'PIC berhasil ditugaskan')

const onPriority = (priority: string) =>
  run(() => updateTicketPriority(props.id, priority), 'Prioritas diperbarui')

const onStatus = (status: string) =>
  run(() => updateTicketStatus(props.id, status), 'Status diperbarui')

function onDueDate() {
  if (!dueDraft.value) return
  run(
    () => updateTicketDueDate(props.id, dayjs(dueDraft.value).toISOString()),
    'Tenggat diperbarui',
  )
}

function onDelete() {
  confirm.require({
    header: 'Hapus ticket?',
    message: `Ticket ${ticket.value?.ticket_number} akan dihapus.`,
    icon: 'pi pi-exclamation-triangle',
    rejectProps: {
      label: 'Batal',
      severity: 'secondary',
      variant: 'text',
      size: 'small',
    },
    acceptProps: {
      label: 'Hapus',
      severity: 'danger',
      size: 'small',
    },
    accept: async () => {
      try {
        await deleteTicket(props.id)
        loading.value = true
        ticket.value = null
        await router.replace({ name: 'tickets' })
        toast.add({ severity: 'success', summary: 'Ticket dihapus', life: 3000 })
      } catch (e) {
        toast.add({
          severity: 'error',
          summary: 'Gagal',
          detail: getErrorMessage(e),
          life: 5000,
        })
      }
    },
  })
}

const errorView = computed(() => {
  switch (errorStatus.value) {
    case 403:
      return {
        icon: 'pi pi-lock',
        title: 'Kamu tidak punya akses ke ticket ini',
        description:
          'Ticket ini milik pengguna lain. Kalau seharusnya kamu bisa melihatnya, hubungi PM IT.',
        retry: false,
      }
    case 404:
      return {
        icon: 'pi pi-search',
        title: 'Ticket tidak ditemukan',
        description: 'Ticket mungkin sudah dihapus atau nomornya salah.',
        retry: false,
      }
    default:
      return {
        icon: 'pi pi-exclamation-triangle',
        title: 'Gagal memuat ticket',
        description: error.value,
        retry: true,
      }
  }
})

const formatDateTime = (iso: string) => dayjs(iso).format('DD MMM YYYY, HH:mm')

function who(
  person: { id: number; name: string } | null | undefined,
  id: number | null,
  empty = '-',
) {
  if (!id) return empty

  const name =
    person?.name ?? staff.value.find((s) => s.id === id)?.name ?? `User #${id}`

  return id === auth.user?.id ? `${name} (Kamu)` : name
}

const details = computed(() => {
  const t = ticket.value
  if (!t) return []

  return [
    { label: 'Jenis', value: t.type },
    { label: 'Company', value: t.company?.name ?? companyName.value },
    { label: 'Aplikasi', value: t.application?.name ?? applicationName.value },
    { label: 'Modul', value: t.module || '-' },
    { label: 'Pelapor', value: who(t.reporter, t.reporter_id) },
    { label: 'PIC', value: who(t.pic, t.pic_id, 'Belum ditugaskan') },
    { label: 'Tenggat', value: t.due_date ? formatDateTime(t.due_date) : '-' },
    { label: 'SLA', value: '', key: 'sla' },
    { label: 'Dibuat', value: formatDateTime(t.created_at) },
  ] as { label: string; value: string; key?: string }[]
})
</script>

<template>
  <div class="mx-auto max-w-5xl px-6 py-6">
    <Button
      label="Kembali"
      icon="pi pi-arrow-left"
      severity="secondary"
      variant="text"
      size="small"
      class="mb-4"
      @click="router.push({ name: 'tickets' })"
    />

    <Message v-if="error && ticket" severity="error" size="small" :closable="false" class="mb-4">
      {{ error }}
    </Message>

    <div v-if="loading" class="flex flex-col gap-4">
      <div class="h-56 animate-pulse rounded-xl bg-slate-100"></div>
      <div class="h-48 animate-pulse rounded-xl bg-slate-100"></div>
    </div>

    <ErrorState
      v-else-if="!ticket"
      :icon="errorView.icon"
      :title="errorView.title"
      :description="errorView.description"
    >
      <Button
        label="Ke daftar ticket"
        icon="pi pi-list"
        size="small"
        @click="router.push({ name: 'tickets' })"
      />
      <Button
        v-if="errorView.retry"
        label="Coba lagi"
        size="small"
        severity="secondary"
        variant="outlined"
        @click="retry"
      />
    </ErrorState>

    <div v-else class="flex flex-col gap-6">
      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex items-start justify-between gap-4">
          <p class="text-sm text-slate-500">{{ ticket.ticket_number }}</p>

          <div class="flex shrink-0 gap-2">
            <StatusBadge :status="ticket.status" />
            <PriorityBadge :priority="ticket.priority" />
          </div>
        </div>

        <h1 class="mt-1 text-xl font-bold text-slate-800">
          {{ ticket.title }}
        </h1>

        <p class="mt-3 text-sm whitespace-pre-wrap text-slate-700">
          {{ ticket.description }}
        </p>

        <dl
          class="mt-6 grid grid-cols-1 gap-x-8 gap-y-4 border-t border-slate-100 pt-5 sm:grid-cols-2 lg:grid-cols-3"
        >
          <div v-for="d in details" :key="d.label">
            <dt class="text-xs text-slate-500">{{ d.label }}</dt>

            <dd class="mt-0.5 text-sm font-medium text-slate-800">
              <SlaBadge
                v-if="d.key === 'sla'"
                :due-date="ticket.due_date"
                :status="ticket.status"
              />
              <template v-else>{{ d.value }}</template>
            </dd>
          </div>
        </dl>

        <div
          v-if="showActions"
          class="mt-6 flex flex-wrap items-end gap-4 border-t border-slate-100 pt-5"
        >
          <div v-if="canManage" class="flex w-full flex-col gap-1.5 sm:w-52">
            <label class="text-xs text-slate-500">Assign ke Staff IT</label>

            <Select
              :model-value="ticket.pic_id"
              :options="staff"
              option-label="name"
              option-value="id"
              placeholder="Pilih Staff IT"
              size="small"
              :disabled="acting"
              fluid
              @update:model-value="onAssign"
            />
          </div>

          <div v-if="canManage" class="flex w-full flex-col gap-1.5 sm:w-40">
            <label class="text-xs text-slate-500">Ubah Prioritas</label>

            <Select
              :model-value="ticket.priority"
              :options="PRIORITY_OPTIONS"
              size="small"
              :disabled="acting"
              fluid
              @update:model-value="onPriority"
            />
          </div>

          <div v-if="canManage" class="flex w-full flex-col gap-1.5 sm:w-72">
            <label class="text-xs text-slate-500">Atur Tenggat</label>

            <div class="flex items-center gap-2">
              <DatePicker
                v-model="dueDraft"
                show-time
                hour-format="24"
                date-format="dd/mm/yy"
                :min-date="minDate"
                :manual-input="false"
                show-icon
                icon-display="input"
                placeholder="Pilih tanggal dan jam"
                size="small"
                :disabled="acting"
                fluid
              />

              <Button
                v-if="dueDirty"
                label="Simpan"
                size="small"
                :loading="acting"
                @click="onDueDate"
              />
            </div>
          </div>

          <div v-if="nextStatuses.length" class="flex w-full flex-col gap-1.5 sm:w-56">
            <label class="text-xs text-slate-500">Ubah Status</label>

            <Select
              :model-value="null"
              :options="nextStatuses"
              placeholder="Pilih status berikutnya"
              size="small"
              :disabled="acting"
              fluid
              @update:model-value="onStatus"
            />
          </div>

          <Button
            v-if="canDelete"
            label="Hapus Ticket"
            icon="pi pi-trash"
            severity="danger"
            variant="text"
            class="sm:ml-auto"
            :disabled="acting"
            @click="onDelete"
          />
        </div>

        <p v-else-if="isDone" class="mt-6 border-t border-slate-100 pt-4 text-xs text-slate-500">
          Ticket sudah selesai dan tidak dapat diubah.
        </p>
      </section>

      <section class="rounded-xl border border-slate-200 bg-white shadow-sm">
        <Tabs value="comments" lazy>
          <TabList>
            <Tab value="comments">Komentar</Tab>
            <Tab value="attachments">Lampiran</Tab>
            <Tab value="history">Riwayat</Tab>
          </TabList>

          <TabPanels>
            <TabPanel value="comments">
              <CommentSection :ticket-id="ticket.id" />
            </TabPanel>

            <TabPanel value="attachments">
              <AttachmentList :ticket-id="ticket.id" :readonly="isDone" />
            </TabPanel>

            <TabPanel value="history">
              <HistoryTimeline
                :key="historyKey"
                :ticket-id="ticket.id"
                :ticket-number="ticket.ticket_number"
              />
            </TabPanel>
          </TabPanels>
        </Tabs>
      </section>
    </div>
  </div>
</template>