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
  type Attachment,
} from '@/api/attachment'
import { getErrorMessage } from '@/api/client'
import { formatFileSize, isImage, isPdf } from '@/utils/format'
import { useAuthStore } from '@/stores/auth'

// Atasan mewajibkan lampiran, jadi yang terakhir tidak boleh dihapus. Set 0 untuk mematikan.
const MIN_ATTACHMENTS = 1

const props = defineProps<{
  ticketId: number
  readonly?: boolean // true = sembunyikan tombol hapus (misalnya tiket sudah Done)
}>()

const auth = useAuthStore()
const confirm = useConfirm()
const toast = useToast()

const items = ref<Attachment[]>([])
const loading = ref(true)
const error = ref('')
const busyId = ref<number | null>(null)

const previewVisible = ref(false)
const previewUrl = ref('')
const previewType = ref('')
const previewName = ref('')

const isPM = computed(() => auth.user?.role === 'PM_IT')
const isLast = computed(() => items.value.length <= MIN_ATTACHMENTS)

// SESUAIKAN dengan aturan backend: pengunggah atau PM IT
const canDelete = (a: Attachment) =>
  !props.readonly && (isPM.value || a.uploaded_by.id === auth.user?.id)

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

onMounted(load)

const iconOf = (a: Attachment) =>
  isImage(a.content_type) ? 'pi pi-image' : isPdf(a.content_type) ? 'pi pi-file-pdf' : 'pi pi-file'

const canPreview = (a: Attachment) => isImage(a.content_type) || isPdf(a.content_type)

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

onBeforeUnmount(onHide)
</script>

<template>
  <div>
    <Message v-if="error" severity="error" size="small" :closable="false" class="mb-3">
      {{ error }}
    </Message>

    <div v-if="loading" class="flex flex-col gap-2">
      <div v-for="n in 3" :key="n" class="h-14 animate-pulse rounded-lg bg-slate-100"></div>
    </div>

    <p v-else-if="!items.length" class="py-6 text-center text-sm text-slate-500">
      Belum ada lampiran.
    </p>

    <ul v-else class="divide-y divide-slate-100 rounded-lg border border-slate-200">
      <li v-for="a in items" :key="a.id" class="flex items-center gap-3 p-3">
        <i :class="iconOf(a)" class="text-xl text-slate-400"></i>
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-medium text-slate-800">{{ a.original_filename }}</p>
          <p class="text-xs text-slate-500">
            {{ formatFileSize(a.file_size) }} · {{ a.uploaded_by.name }} ·
            {{ dayjs(a.created_at).format('DD MMM YYYY, HH:mm') }}
          </p>
        </div>

        <Button
          v-if="canPreview(a)"
          icon="pi pi-eye"
          severity="secondary"
          variant="text"
          size="small"
          aria-label="Pratinjau"
          :loading="busyId === a.id"
          @click="onPreview(a)"
        />
        <Button
          icon="pi pi-download"
          severity="secondary"
          variant="text"
          size="small"
          aria-label="Unduh"
          :disabled="busyId === a.id"
          @click="onDownload(a)"
        />
        <Button
          v-if="canDelete(a)"
          icon="pi pi-trash"
          severity="danger"
          variant="text"
          size="small"
          :aria-label="isLast ? 'Lampiran terakhir tidak bisa dihapus' : 'Hapus'"
          :title="isLast ? 'Ticket harus punya minimal satu lampiran' : 'Hapus lampiran'"
          :disabled="busyId === a.id || isLast"
          @click="onDelete(a)"
        />
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