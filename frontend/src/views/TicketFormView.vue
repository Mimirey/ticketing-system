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
import { getErrorMessage } from '@/api/client'
import { PRIORITY_OPTIONS, TYPE_OPTIONS } from '@/constant/ticket'

const MIN_DESCRIPTION = 10 // SESUAIKAN dengan schema backend
const MAX_FILES = 5 // SESUAIKAN
const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5 MB, SESUAIKAN
const ACCEPT = 'image/*,.pdf,.doc,.docx,.xls,.xlsx,.txt' // SESUAIKAN
const fileUploadRef = ref<{ choose: () => void } | null>(null)

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
const uploaded = new Set<File>()
const locked = computed(() => !!createdTicket.value)

for (const key of Object.keys(errors) as (keyof typeof errors)[]) {
  watch(() => form[key], () => (errors[key] = ''))
}

function onFilesChange(e: { files: File[] }) {
  files.value = [...e.files]
  fileError.value = ''
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
  errors.title = form.title.trim() ? '' : 'Judul wajib diisi'
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
    submitError.value = getErrorMessage(e, 'Gagal membuat ticket')
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
                :disabled="locked"
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
                    :disabled="locked"
                    @click="chooseCallback()"
                    />
                </div>
                </template>

                <template #empty>
                <div class="flex flex-col items-center gap-4 py-4 text-center">
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