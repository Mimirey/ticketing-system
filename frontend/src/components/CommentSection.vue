<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import dayjs from 'dayjs'
import { useConfirm } from 'primevue/useconfirm'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import Message from 'primevue/message'
import Textarea from 'primevue/textarea'
import {
  createComment,
  deleteComment,
  fetchComments,
  updateComment,
  type TicketComment,
} from '@/api/comment'
import { getErrorMessage } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{ ticketId: number }>()

const auth = useAuthStore()
const confirm = useConfirm()

const comments = ref<TicketComment[]>([])
const loading = ref(true)
const error = ref('')

const newText = ref('')
const posting = ref(false)

const editingId = ref<number | null>(null)
const editText = ref('')
const saving = ref(false)

// Komentar terbaru di atas
const sorted = computed(() =>
  [...comments.value].sort((a, b) => dayjs(b.created_at).valueOf() - dayjs(a.created_at).valueOf()),
)

async function load() {
  error.value = ''
  try {
    comments.value = await fetchComments(props.ticketId)
  } catch (e) {
    error.value = getErrorMessage(e, 'Gagal memuat komentar')
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function onPost() {
  const text = newText.value.trim()
  if (!text) return
  posting.value = true
  error.value = ''
  try {
    await createComment(props.ticketId, text)
    newText.value = ''
    await load()
  } catch (e) {
    error.value = getErrorMessage(e, 'Gagal mengirim komentar')
  } finally {
    posting.value = false
  }
}

function startEdit(c: TicketComment) {
  editingId.value = c.id
  editText.value = c.content
}

async function onSaveEdit(c: TicketComment) {
  const text = editText.value.trim()
  if (!text) return
  saving.value = true
  error.value = ''
  try {
    await updateComment(props.ticketId, c.id, text)
    editingId.value = null
    await load()
  } catch (e) {
    error.value = getErrorMessage(e, 'Gagal menyimpan perubahan')
  } finally {
    saving.value = false
  }
}

function onDelete(c: TicketComment) {
  confirm.require({
    header: 'Hapus komentar?',
    message: 'Komentar ini akan dihapus.',
    icon: 'pi pi-exclamation-triangle',
    rejectProps: { label: 'Batal', severity: 'secondary', variant: 'text', size: 'small' },
    acceptProps: { label: 'Hapus', severity: 'danger', size: 'small' },
    accept: async () => {
      try {
        await deleteComment(props.ticketId, c.id)
        await load()
      } catch (e) {
        error.value = getErrorMessage(e, 'Gagal menghapus komentar')
      }
    },
  })
}

const isMine = (c: TicketComment) => c.author.id === auth.user?.id

const initials = (name: string) =>
  name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase())
    .join('')

const formatTime = (iso: string) => dayjs(iso).format('DD MMM YYYY, HH:mm')
</script>

<template>
  <div class="flex flex-col gap-5">
    <!-- Form komentar baru -->
    <div class="flex flex-col gap-2">
      <Textarea
        v-model="newText"
        rows="3"
        placeholder="Tulis komentar..."
        :disabled="posting"
        fluid
      />
      <div class="flex justify-end">
        <Button
          label="Kirim"
          icon="pi pi-send"
          size="small"
          :loading="posting"
          :disabled="!newText.trim()"
          @click="onPost"
        />
      </div>
    </div>

    <Message v-if="error" severity="error" size="small" :closable="false">{{ error }}</Message>

    <div v-if="loading" class="flex flex-col gap-3">
      <div v-for="n in 2" :key="n" class="h-16 animate-pulse rounded-lg bg-slate-100"></div>
    </div>

    <div v-else-if="!sorted.length" class="flex flex-col items-center gap-2 py-6 text-center">
      <i class="pi pi-comments text-3xl text-slate-300"></i>
      <p class="text-sm text-slate-500">Belum ada komentar. Jadilah yang pertama.</p>
    </div>

    <ul v-else class="flex flex-col gap-5">
      <li v-for="c in sorted" :key="c.id" class="flex gap-3">
        <Avatar
          :label="initials(c.author.name)"
          shape="circle"
          class="shrink-0 bg-(--p-primary-50)! text-(--p-primary-color)!"
        />

        <div class="min-w-0 flex-1">
          <div class="flex flex-wrap items-center gap-x-2 text-sm">
            <span class="font-semibold text-slate-800">{{ c.author.name }}</span>
            <span class="text-xs text-slate-500">
              {{ formatTime(c.created_at) }}<template v-if="c.edited"> · diubah</template>
            </span>
          </div>

          <!-- Mode edit -->
          <div v-if="editingId === c.id" class="mt-2 flex flex-col gap-2">
            <Textarea v-model="editText" rows="3" :disabled="saving" fluid />
            <div class="flex gap-2">
              <Button
                label="Simpan"
                size="small"
                :loading="saving"
                :disabled="!editText.trim()"
                @click="onSaveEdit(c)"
              />
              <Button
                label="Batal"
                size="small"
                severity="secondary"
                variant="text"
                :disabled="saving"
                @click="editingId = null"
              />
            </div>
          </div>

          <!-- Mode baca -->
          <template v-else>
            <p class="mt-1 text-sm whitespace-pre-wrap text-slate-700">{{ c.content }}</p>
            <div v-if="isMine(c)" class="mt-1 flex gap-3 text-xs">
              <button
                type="button"
                class="text-slate-500 hover:text-(--p-primary-color)"
                @click="startEdit(c)"
              >
                Ubah
              </button>
              <button
                type="button"
                class="text-slate-500 hover:text-red-600"
                @click="onDelete(c)"
              >
                Hapus
              </button>
            </div>
          </template>
        </div>
      </li>
    </ul>
  </div>
</template>