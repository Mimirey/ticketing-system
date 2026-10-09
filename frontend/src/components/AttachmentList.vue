<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import dayjs from 'dayjs'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Message from 'primevue/message'
import {
  deleteAttachment,
  downloadAttachment,
  fetchAttachments,
  getPreviewUrl,
  uploadAttachment,
  type Attachment,
} from '@/api/attachment'
import { getErrorMessage } from '@/api/client'
import { formatFileSize, isImage, isPdf } from '@/utils/format'
import { useAuthStore } from '@/stores/auth'

const MIN_ATTACHMENTS = 1
const MAX_FILE_SIZE = 5 * 1024 * 1024
const ACCEPT = 'image/*,.pdf,.doc,.docx,.xls,.xlsx,.txt'
const ALLOWED_EXT = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt']

const props = defineProps<{
  ticketId: number
  reporterId: number
  readonly?: boolean
}>()

const auth = useAuthStore()
const confirm = useConfirm()
const toast = useToast()

const items = ref<Attachment[]>([])
const loading = ref(true)
const error = ref('')
const busyId = ref<number | null>(null)

const uploading = ref(false)
const uploadErrors = ref<string[]>([])
const dragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const previewVisible = ref(false)
const previewUrl = ref('')
const previewType = ref('')
const previewName = ref('')

const isReporter = computed(() => !!auth.user && auth.user.id === props.reporterId)
const canManage = computed(() => !props.readonly && isReporter.value)
const isLast = computed(() => items.value.length <= MIN_ATTACHMENTS)

const canPreview = (a: Attachment) => isImage(a.content_type) || isPdf(a.content_type)

const iconOf = (a: Attachment) =>
  isImage(a.content_type) ? 'pi pi-image' : isPdf(a.content_type) ? 'pi pi-file-pdf' : 'pi pi-file'

const iconBoxOf = (a: Attachment) =>
  isImage(a.content_type)
    ? 'bg-sky-50 text-sky-600'
    : isPdf(a.content_type)
      ? 'bg-red-50 text-red-600'
      : 'bg-slate-100 text-slate-500'

function isAllowed(file: File): boolean {
  if (file.type.startsWith('image/')) return true
  const name = file.name.toLowerCase()
  return ALLOWED_EXT.some((ext) => name.endsWith(ext))
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    items.value = await fetchAttachments(props.ticketId)
  } catch (e) {
    error.value = getErrorMessage(e, 'Gagal memuat lampiran')
  } finally {
    loading.value = false
  }
}

async function uploadFiles(list: File[]) {
  if (!list.length || uploading.value || !canManage.value) return

  uploadErrors.value = []
  const problems: string[] = []
  const valid: File[] = []

  for (const file of list) {
    if (!isAllowed(file)) problems.push(`${file.name}: tipe file tidak didukung`)
    else if (file.size > MAX_FILE_SIZE) problems.push(`${file.name}: ukuran melebihi 5 MB`)
    else valid.push(file)
  }

  uploading.value = true
  let success = 0

  for (const file of valid) {
    try {
      const attachment = await uploadAttachment(props.ticketId, file)
      items.value.push(attachment)
      success++
    } catch (e) {
      problems.push(`${file.name}: ${getErrorMessage(e, 'gagal diunggah')}`)
    }
  }

  uploading.value = false
  uploadErrors.value = problems

  if (success) {
    toast.add({
      severity: 'success',
      summary: success === 1 ? 'Lampiran berhasil diunggah' : `${success} lampiran berhasil diunggah`,
      life: 3000,
    })
  }
}

function pickFiles() {
  if (!uploading.value) fileInput.value?.click()
}

function onInputChange(event: Event) {
  const input = event.target as HTMLInputElement
  const list = Array.from(input.files ?? [])
  input.value = ''
  uploadFiles(list)
}

function onDrop(event: DragEvent) {
  dragging.value = false
  uploadFiles(Array.from(event.dataTransfer?.files ?? []))
}

async function onPreview(a: Attachment) {
  busyId.value = a.id
  error.value = ''
  try {
    previewUrl.value = await getPreviewUrl(props.ticketId, a)
    previewType.value = a.content_type
    previewName.value = a.original_filename
    previewVisible.value = true
  } catch (e) {
    error.value = getErrorMessage(e, 'Gagal membuka pratinjau')
  } finally {
    busyId.value = null
  }
}

async function onDownload(a: Attachment) {
  busyId.value = a.id
  error.value = ''
  try {
    await downloadAttachment(props.ticketId, a)
  } catch (e) {
    error.value = getErrorMessage(e, 'Gagal mengunduh lampiran')
  } finally {
    busyId.value = null
  }
}

function onDelete(a: Attachment) {
  confirm.require({
    header: 'Hapus lampiran?',
    message: `"${a.original_filename}" akan dihapus dari ticket ini.`,
    icon: 'pi pi-exclamation-triangle',
    rejectProps: { label: 'Batal', severity: 'secondary', variant: 'text', size: 'small' },
    acceptProps: { label: 'Hapus', severity: 'danger', size: 'small' },
    accept: async () => {
      busyId.value = a.id
      error.value = ''
      try {
        await deleteAttachment(props.ticketId, a.id)
        items.value = items.value.filter((x) => x.id !== a.id)
        toast.add({ severity: 'success', summary: 'Lampiran dihapus', life: 3000 })
      } catch (e) {
        error.value = getErrorMessage(e, 'Gagal menghapus lampiran')
      } finally {
        busyId.value = null
      }
    },
  })
}

function onHide() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ''
}

onMounted(load)
onBeforeUnmount(onHide)
</script>

<template>
  <div class="flex flex-col gap-3">
    <Message v-if="error" severity="error" size="small" :closable="false">
      {{ error }}
    </Message>

    <Message v-if="uploadErrors.length" severity="error" size="small" :closable="false">
      <ul class="flex flex-col gap-0.5">
        <li v-for="msg in uploadErrors" :key="msg">{{ msg }}</li>
      </ul>
    </Message>

    <div
      v-if="canManage"
      class="flex items-center gap-3 rounded-lg border border-dashed px-3 py-2.5 transition-colors"
      :class="
        dragging
          ? 'border-(--p-primary-color) bg-(--p-primary-50)'
          : 'border-slate-300 bg-slate-50/60'
      "
      @dragover.prevent="dragging = true"
      @dragleave.prevent="dragging = false"
      @drop.prevent="onDrop"
    >

        <i class="pi pi-cloud-upload"></i>

      <div class="min-w-0 flex-1">
        <p class="text-sm font-medium text-slate-800">Seret file ke sini atau pilih dari perangkat</p>
        <p class="text-xs text-slate-500">
          maks. {{ MAX_FILE_SIZE / 1024 / 1024 }} MB per file
        </p>
      </div>

      <input
        ref="fileInput"
        type="file"
        multiple
        class="hidden"
        :accept="ACCEPT"
        @change="onInputChange"
      />

      <Button
        type="button"
        label="Pilih file"
        icon="pi pi-paperclip"
        size="small"
        variant="outlined"
        :loading="uploading"
        @click="pickFiles"
      />
    </div>

    <div class="flex items-center justify-between px-0.5">
      <h3 class="text-xs font-semibold tracking-wide text-slate-500 uppercase">
        Lampiran
        <span class="ml-1 rounded-full bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">
          {{ items.length }}
        </span>
      </h3>
    </div>

    <div v-if="loading" class="flex flex-col gap-2">
      <div v-for="n in 2" :key="n" class="h-12 animate-pulse rounded-lg bg-slate-100"></div>
    </div>

    <div
      v-else-if="!items.length"
      class="flex flex-col items-center gap-1 rounded-lg border border-slate-200 py-6 text-center"
    >
      <i class="pi pi-paperclip text-xl text-slate-300"></i>
      <p class="text-sm text-slate-500">Belum ada lampiran.</p>
    </div>

    <ul v-else class="divide-y divide-slate-100 overflow-hidden rounded-lg border border-slate-200">
      <li
        v-for="a in items"
        :key="a.id"
        class="flex items-center gap-3 px-3 py-2 transition-colors hover:bg-slate-50"
      >
        <div
          class="flex h-8 w-8 shrink-0 items-center justify-center rounded-md"
          :class="iconBoxOf(a)"
        >
          <i :class="iconOf(a)"></i>
        </div>

        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-medium text-slate-800" :title="a.original_filename">
            {{ a.original_filename }}
          </p>
          <p class="truncate text-xs text-slate-500">
            {{ formatFileSize(a.file_size) }} · {{ a.uploaded_by.name }} ·
            {{ dayjs(a.created_at).format('DD MMM YYYY, HH:mm') }}
          </p>
        </div>

        <div class="flex shrink-0 items-center">
          <Button
            v-if="canPreview(a)"
            icon="pi pi-eye"
            severity="secondary"
            variant="text"
            rounded
            size="small"
            aria-label="Pratinjau"
            :loading="busyId === a.id"
            :disabled="uploading"
            @click="onPreview(a)"
          />

          <Button
            icon="pi pi-download"
            severity="secondary"
            variant="text"
            rounded
            size="small"
            aria-label="Unduh"
            :disabled="busyId === a.id || uploading"
            @click="onDownload(a)"
          />

          <Button
            v-if="canManage"
            icon="pi pi-trash"
            severity="danger"
            variant="text"
            rounded
            size="small"
            :aria-label="isLast ? 'Lampiran terakhir tidak bisa dihapus' : 'Hapus lampiran'"
            :title="isLast ? 'Ticket harus punya minimal satu lampiran' : 'Hapus lampiran'"
            :disabled="busyId === a.id || isLast || uploading"
            @click="onDelete(a)"
          />
        </div>
      </li>
    </ul>

    <Dialog
      v-model:visible="previewVisible"
      :header="previewName"
      modal
      :style="{ width: '60rem', maxWidth: '95vw' }"
      @hide="onHide"
    >
      <img
        v-if="isImage(previewType)"
        :src="previewUrl"
        :alt="previewName"
        class="mx-auto max-h-[70vh] object-contain"
      />

      <iframe v-else :src="previewUrl" class="h-[70vh] w-full" title="Pratinjau lampiran"></iframe>
    </Dialog>
  </div>
</template>