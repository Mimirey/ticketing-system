<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import FileUpload from 'primevue/fileupload'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { createTicket, type Ticket } from '@/api/ticket'
import { uploadAttachment } from '@/api/attachment'
import { fetchApplications, fetchCompanies, type Application, type Company } from '@/api/master'
import { getErrorMessage, getFieldErrors } from '@/api/client'
import { PRIORITY_OPTIONS, TYPE_OPTIONS } from '@/constant/ticket'
import { formatFileSize } from '@/utils/format'

const MIN_DESCRIPTION = 10
const MIN_TITLE = 5
const MAX_FILES = 5
const MAX_FILE_SIZE = 5 * 1024 * 1024
const ACCEPT = 'image/*,.pdf,.doc,.docx,.xls,.xlsx,.txt'

const router = useRouter()
const toast = useToast()

const form = reactive({
  type: 'Bug' as string | null,
  priority: 'Low' as string | null,
  title: '',
  module: '',
  description: '',
  companyId: null as number | null,
  applicationId: null as number | null,
})

const errors = reactive({
  type: '',
  priority: '',
  title: '',
  description: '',
  companyId: '',
  applicationId: '',
})

const files = ref<File[]>([])
const fileError = ref('')

const companies = ref<Company[]>([])
const applications = ref<Application[]>([])
const loadingCompanies = ref(false)
const loadingApplications = ref(false)
const submitting = ref(false)
const submitError = ref('')

const createdTicket = ref<Ticket | null>(null)
const uploaded = reactive(new Set<File>())
const locked = computed(() => !!createdTicket.value)

for (const key of Object.keys(errors) as (keyof typeof errors)[]) {
  watch(
    () => form[key],
    () => (errors[key] = ''),
  )
}

function onFilesChange(e: { files: File[] }) {
  files.value = [...e.files]
  fileError.value = ''
}

function getFileObjectURL(file: File): string | undefined {
  return (file as File & { objectURL?: string }).objectURL
}

onMounted(async () => {
  loadingCompanies.value = true
  try {
    companies.value = await fetchCompanies()
  } catch (e) {
    submitError.value = getErrorMessage(e, 'Gagal memuat daftar company')
  } finally {
    loadingCompanies.value = false
  }
})

watch(
  () => form.companyId,
  async (id) => {
    form.applicationId = null
    applications.value = []
    if (!id) return

    loadingApplications.value = true
    try {
      applications.value = await fetchApplications(id)
    } catch (e) {
      submitError.value = getErrorMessage(e, 'Gagal memuat daftar aplikasi')
    } finally {
      loadingApplications.value = false
    }
  },
)

function validate(): boolean {
  errors.type = form.type ? '' : 'Jenis ticket wajib dipilih'
  errors.priority = form.priority ? '' : 'Prioritas wajib dipilih'

  const title = form.title.trim()
  if (!title) errors.title = 'Judul wajib diisi'
  else if (title.length < MIN_TITLE) errors.title = `Judul minimal ${MIN_TITLE} karakter`
  else errors.title = ''

  errors.companyId = form.companyId ? '' : 'Company wajib dipilih'
  errors.applicationId = form.applicationId ? '' : 'Aplikasi wajib dipilih'

  const desc = form.description.trim()
  if (!desc) errors.description = 'Deskripsi wajib diisi'
  else if (desc.length < MIN_DESCRIPTION)
    errors.description = `Deskripsi minimal ${MIN_DESCRIPTION} karakter`
  else errors.description = ''

  fileError.value = files.value.length ? '' : 'Minimal satu lampiran wajib diunggah'

  return Object.values(errors).every((m) => !m) && !fileError.value
}

const FORM_KEYS: Record<string, keyof typeof errors> = {
  type: 'type',
  priority: 'priority',
  title: 'title',
  description: 'description',
  company_id: 'companyId',
  application_id: 'applicationId',
}

function applyFieldErrors(error: unknown): boolean {
  let applied = false

  for (const [key, message] of Object.entries(getFieldErrors(error))) {
    const target = FORM_KEYS[key]

    if (target) {
      errors[target] = message
      applied = true
    }
  }

  return applied
}

async function onSubmit() {
  submitError.value = ''
  if (!validate()) return

  submitting.value = true
  try {
    if (!createdTicket.value) {
      createdTicket.value = await createTicket({
        type: form.type!,
        priority: form.priority!,
        title: form.title.trim(),
        description: form.description.trim(),
        module: form.module.trim() || undefined,
        company_id: form.companyId!,
        application_id: form.applicationId!,
      })
    }

    const ticket = createdTicket.value

    const pending = files.value.filter((f) => !uploaded.has(f))
    const results = await Promise.allSettled(
      pending.map((f) => uploadAttachment(ticket.id, f).then(() => uploaded.add(f))),
    )
    const failed = results.filter((r) => r.status === 'rejected').length

    if (failed > 0) {
      submitError.value = `Ticket ${ticket.ticket_number} sudah dibuat, tetapi ${failed} lampiran gagal diunggah. Klik "Coba unggah lagi".`
      return
    }

    toast.add({
      severity: 'success',
      summary: 'Ticket berhasil dibuat',
      detail: `Nomor ${ticket.ticket_number}`,
      life: 4000,
    })

    router.push({ name: 'tickets' })
  } catch (e) {
    submitError.value = applyFieldErrors(e)
      ? 'Periksa kembali isian yang ditandai.'
      : getErrorMessage(e, 'Gagal membuat ticket')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl p-6">
    <h1 class="mb-6 text-xl font-bold text-slate-800">Buat Ticket Baru</h1>

    <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <form class="flex flex-col gap-6" novalidate @submit.prevent="onSubmit">
        <Message v-if="submitError" severity="error" size="small" :closable="false">
          {{ submitError }}
        </Message>

        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div class="flex flex-col gap-2">
            <label for="type" class="text-sm font-medium text-slate-800">Jenis Ticket</label>
            <Select
              v-model="form.type"
              input-id="type"
              :options="TYPE_OPTIONS"
              size="small"
              :disabled="locked"
              :invalid="!!errors.type"
              fluid
            />
            <Message v-if="errors.type" severity="error" size="small" variant="simple">
              {{ errors.type }}
            </Message>
          </div>

          <div class="flex flex-col gap-2">
            <label for="priority" class="text-sm font-medium text-slate-800">Prioritas</label>
            <Select
              v-model="form.priority"
              input-id="priority"
              :options="PRIORITY_OPTIONS"
              size="small"
              :disabled="locked"
              :invalid="!!errors.priority"
              fluid
            />
            <Message v-if="errors.priority" severity="error" size="small" variant="simple">
              {{ errors.priority }}
            </Message>
          </div>

          <div class="flex flex-col gap-2">
            <label for="company" class="text-sm font-medium text-slate-800">Company</label>
            <Select
              v-model="form.companyId"
              input-id="company"
              :options="companies"
              option-label="name"
              option-value="id"
              placeholder="Pilih company"
              :loading="loadingCompanies"
              :disabled="locked"
              filter
              size="small"
              :invalid="!!errors.companyId"
              fluid
            />
            <Message v-if="errors.companyId" severity="error" size="small" variant="simple">
              {{ errors.companyId }}
            </Message>
          </div>

          <div class="flex flex-col gap-2">
            <label for="application" class="text-sm font-medium text-slate-800">Aplikasi</label>
            <Select
              v-model="form.applicationId"
              input-id="application"
              :options="applications"
              option-label="name"
              option-value="id"
              :placeholder="form.companyId ? 'Pilih aplikasi' : 'Pilih company dulu'"
              :disabled="!form.companyId || locked"
              :loading="loadingApplications"
              filter
              size="small"
              :invalid="!!errors.applicationId"
              fluid
            />
            <Message v-if="errors.applicationId" severity="error" size="small" variant="simple">
              {{ errors.applicationId }}
            </Message>
          </div>
        </div>

        <div class="flex flex-col gap-2">
          <label for="title" class="text-sm font-medium text-slate-800">Judul</label>
          <InputText
            id="title"
            v-model="form.title"
            placeholder="Ringkasan singkat masalah/permintaan"
            size="small"
            :disabled="locked"
            :invalid="!!errors.title"
            fluid
          />
          <Message v-if="errors.title" severity="error" size="small" variant="simple">
            {{ errors.title }}
          </Message>
        </div>

        <div class="flex flex-col gap-2">
          <label for="module" class="text-sm font-medium text-slate-800">
            Modul Aplikasi <span class="font-normal text-slate-400">(opsional)</span>
          </label>
          <InputText
            id="module"
            v-model="form.module"
            placeholder="Contoh: Login, Dashboard, Pembayaran"
            size="small"
            :disabled="locked"
            fluid
          />
        </div>

        <div class="flex flex-col gap-2">
          <label for="description" class="text-sm font-medium text-slate-800">Deskripsi</label>
          <Textarea
            id="description"
            v-model="form.description"
            rows="6"
            placeholder="Jelaskan detail masalah atau permintaan fitur..."
            size="small"
            :disabled="locked"
            :invalid="!!errors.description"
            fluid
          />
          <Message v-if="errors.description" severity="error" size="small" variant="simple">
            {{ errors.description }}
          </Message>
        </div>

        <div class="flex flex-col gap-2">
          <span class="text-sm font-medium text-slate-800">Lampiran</span>

          <FileUpload
            mode="advanced"
            multiple
            :accept="ACCEPT"
            :max-file-size="MAX_FILE_SIZE"
            :file-limit="MAX_FILES"
            :disabled="submitting"
            invalid-file-size-message="{0}: ukuran file maksimal {1}."
            invalid-file-limit-message="Maksimal {0} file."
            :pt="{
              header: { class: 'p-3!' },
              content: { class: 'p-3!' },
            }"
            @select="onFilesChange"
            @remove="onFilesChange"
          >
            <template #header="{ chooseCallback }">
              <div class="flex flex-wrap items-center gap-3">
                <Button
                  type="button"
                  label="Pilih file"
                  icon="pi pi-paperclip"
                  size="small"
                  :disabled="submitting"
                  @click="chooseCallback()"
                />
              </div>
            </template>

            <template #content="{ files, removeFileCallback }">
              <ul v-if="files.length" class="divide-y divide-slate-100">
                <li
                  v-for="(file, index) in files"
                  :key="file.name + file.size"
                  class="flex items-center gap-3 py-2.5"
                >
                  <img
                    v-if="getFileObjectURL(file) && file.type.startsWith('image/')"
                    :src="getFileObjectURL(file)"
                    :alt="file.name"
                    class="h-10 w-10 shrink-0 rounded-md border border-slate-200 bg-white object-contain"
                  />
                  <i v-else class="pi pi-file text-xl text-slate-400"></i>

                  <div class="min-w-0 flex-1">
                    <p class="truncate text-sm font-medium text-slate-800">{{ file.name }}</p>
                    <p class="text-xs text-slate-500">{{ formatFileSize(file.size) }}</p>
                  </div>

                  <Button
                    type="button"
                    icon="pi pi-times"
                    severity="secondary"
                    variant="text"
                    rounded
                    size="small"
                    aria-label="Hapus file"
                    :disabled="submitting || uploaded.has(file)"
                    @click="removeFileCallback(index)"
                  />
                </li>
              </ul>

              <div v-else class="flex flex-col items-center gap-2 py-4 text-center">
                <i class="pi pi-paperclip text-3xl text-slate-400"></i>
                <p class="text-sm text-slate-500">Seret file ke sini untuk melampirkan</p>
              </div>
            </template>
          </FileUpload>

          <p class="text-xs text-slate-500">
            Wajib, min. 1 file. Maks. {{ MAX_FILES }} file, masing-masing
            {{ MAX_FILE_SIZE / 1024 / 1024 }} MB.
          </p>

          <Message v-if="fileError" severity="error" size="small" variant="simple">
            {{ fileError }}
          </Message>
        </div>

        <div class="flex items-center gap-2">
          <Button
            type="submit"
            :label="createdTicket ? 'Coba unggah lagi' : 'Buat Ticket'"
            size="small"
            :loading="submitting"
          />
          <Button
            type="button"
            :label="createdTicket ? 'Selesai' : 'Batal'"
            severity="secondary"
            variant="text"
            size="small"
            :disabled="submitting"
            @click="router.push({ name: 'tickets' })"
          />
        </div>
      </form>
    </div>
  </div>
</template>