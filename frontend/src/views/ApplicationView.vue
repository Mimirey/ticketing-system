<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Select from 'primevue/select'
import Button from 'primevue/button'
import Message from 'primevue/message'
import {
  createApplication,
  deleteApplication,
  fetchAllApplications,
  fetchCompanies,
  updateApplication,
  type Application,
  type Company,
} from '@/api/master'
import { getErrorMessage, getErrorStatus, getFieldErrors } from '@/api/client'

const PAGE_SIZE = 10

const toast = useToast()
const confirm = useConfirm()

const applications = ref<Application[]>([])
const companies = ref<Company[]>([])
const loading = ref(true)
const error = ref('')
const keyword = ref('')
const filterCompany = ref<number | null>(null)

const dialogVisible = ref(false)
const editing = ref<Application | null>(null)
const saving = ref(false)
const saveError = ref('')
const deletingId = ref<number | null>(null)

const form = reactive({
  companyId: null as number | null,
  name: '',
  description: '',
})

const errors = reactive({
  companyId: '',
  name: '',
  description: '',
})

const companyNames = computed(() => new Map(companies.value.map((c) => [c.id, c.name])))
const companyName = (id: number) => companyNames.value.get(id) ?? '-'

const filtered = computed(() => {
  const k = keyword.value.trim().toLowerCase()

  return applications.value
    .filter((a) => !filterCompany.value || a.company_id === filterCompany.value)
    .filter(
      (a) =>
        !k ||
        a.name.toLowerCase().includes(k) ||
        (a.description ?? '').toLowerCase().includes(k),
    )
    .sort(
      (a, b) =>
        companyName(a.company_id).localeCompare(companyName(b.company_id), 'id') ||
        a.name.localeCompare(b.name, 'id'),
    )
})

watch(
  () => form.companyId,
  () => (errors.companyId = ''),
)
watch(
  () => form.name,
  () => (errors.name = ''),
)
watch(
  () => form.description,
  () => (errors.description = ''),
)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [apps, comps] = await Promise.all([fetchAllApplications(), fetchCompanies()])
    applications.value = apps
    companies.value = comps
  } catch (e) {
    error.value = getErrorMessage(e, 'Gagal memuat daftar aplikasi')
  } finally {
    loading.value = false
  }
}

onMounted(load)

function resetForm() {
  editing.value = null
  form.companyId = null
  form.name = ''
  form.description = ''
  errors.companyId = ''
  errors.name = ''
  errors.description = ''
  saveError.value = ''
}

function openCreate() {
  resetForm()
  form.companyId = filterCompany.value
  dialogVisible.value = true
}

function openEdit(app: Application) {
  resetForm()
  editing.value = app
  form.companyId = app.company_id
  form.name = app.name
  form.description = app.description ?? ''
  dialogVisible.value = true
}

function validate(): boolean {
  const name = form.name.trim()

  errors.companyId = form.companyId ? '' : 'Company wajib dipilih'

  if (!name) {
    errors.name = 'Nama aplikasi wajib diisi'
  } else if (
    applications.value.some(
      (a) =>
        a.id !== editing.value?.id &&
        a.company_id === form.companyId &&
        a.name.trim().toLowerCase() === name.toLowerCase(),
    )
  ) {
    errors.name = 'Nama aplikasi sudah ada di company ini'
  } else {
    errors.name = ''
  }

  return !errors.companyId && !errors.name
}

async function onSave() {
  saveError.value = ''
  if (!validate()) return

  saving.value = true
  try {
    const payload = {
      company_id: form.companyId!,
      name: form.name.trim(),
      description: form.description.trim(),
    }
    const isEdit = !!editing.value

    if (editing.value) await updateApplication(editing.value.id, payload)
    else await createApplication(payload)

    toast.add({
      severity: 'success',
      summary: isEdit ? 'Aplikasi diperbarui' : 'Aplikasi ditambahkan',
      life: 3000,
    })
    dialogVisible.value = false
    await load()
  } catch (e) {
    const fields = getFieldErrors(e)
    let applied = false

    if (fields.company_id) {
      errors.companyId = fields.company_id
      applied = true
    }
    if (fields.name) {
      errors.name = fields.name
      applied = true
    }
    if (fields.description) {
      errors.description = fields.description
      applied = true
    }

    if (!applied) saveError.value = getErrorMessage(e, 'Gagal menyimpan aplikasi')
  } finally {
    saving.value = false
  }
}

function onDelete(app: Application) {
  confirm.require({
    header: 'Hapus aplikasi?',
    message: `"${app.name}" akan dihapus permanen. Pastikan aplikasi ini tidak lagi dipakai oleh ticket.`,
    icon: 'pi pi-exclamation-triangle',
    rejectProps: { label: 'Batal', severity: 'secondary', variant: 'text', size: 'small' },
    acceptProps: { label: 'Hapus', severity: 'danger', size: 'small' },
    accept: async () => {
      deletingId.value = app.id
      try {
        await deleteApplication(app.id)
        toast.add({ severity: 'success', summary: 'Aplikasi dihapus', life: 3000 })
        await load()
      } catch (e) {
        const status = getErrorStatus(e)
        toast.add({
          severity: 'error',
          summary: 'Gagal menghapus',
          detail:
            status === 500 || status === 409
              ? 'Aplikasi tidak bisa dihapus saat ini. Kemungkinan masih dipakai oleh ticket, atau ada kendala di server.'
              : getErrorMessage(e),
          life: 6000,
        })
      } finally {
        deletingId.value = null
      }
    },
  })
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-6 py-6">
    <div class="mb-6 flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-xl font-bold text-slate-800">Aplikasi</h1>
        <p class="mt-1 text-sm text-slate-500">
          Kelola aplikasi di setiap company yang bisa dipilih saat membuat ticket
        </p>
      </div>

      <Button
        label="Tambah Aplikasi"
        icon="pi pi-plus"
        size="small"
        :disabled="!companies.length"
        @click="openCreate"
      />
    </div>

    <Message
      v-if="!loading && !error && !companies.length"
      severity="info"
      size="small"
      :closable="false"
      class="mb-4"
    >
      Belum ada company. Tambahkan company terlebih dahulu di menu Company.
    </Message>

    <div class="mb-4 flex flex-wrap items-center gap-2">
      <IconField class="w-full sm:w-72">
        <InputIcon class="pi pi-search" />
        <InputText v-model="keyword" placeholder="Cari aplikasi" size="small" fluid />
      </IconField>

      <Select
        v-model="filterCompany"
        :options="companies"
        option-label="name"
        option-value="id"
        placeholder="Semua Company"
        show-clear
        filter
        size="small"
        class="w-56"
      />
    </div>

    <Message v-if="error" severity="error" size="small" :closable="false" class="mb-4">
      <div class="flex items-center gap-3">
        <span>{{ error }}</span>
        <Button label="Coba lagi" size="small" variant="text" @click="load" />
      </div>
    </Message>

    <div class="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <DataTable
        :value="filtered"
        :loading="loading"
        size="small"
        data-key="id"
        :paginator="filtered.length > PAGE_SIZE"
        :rows="PAGE_SIZE"
        class="text-sm! [&_th]:py-2.5! [&_th]:text-xs! [&_th]:font-semibold! [&_th]:text-slate-500! [&_td]:py-2!"
      >
        <Column field="name" header="Nama Aplikasi" />

        <Column header="Company">
          <template #body="{ data }">{{ companyName(data.company_id) }}</template>
        </Column>

        <Column header="Deskripsi">
          <template #body="{ data }">
            <span v-if="data.description" class="line-clamp-2 max-w-xs text-slate-600">
              {{ data.description }}
            </span>
            <span v-else class="text-slate-400">-</span>
          </template>
        </Column>

        <Column header="Aksi" style="width: 8rem">
          <template #body="{ data }">
            <div class="flex gap-1">
              <Button
                icon="pi pi-pencil"
                severity="secondary"
                variant="text"
                rounded
                size="small"
                aria-label="Ubah"
                @click="openEdit(data)"
              />
              <Button
                icon="pi pi-trash"
                severity="danger"
                variant="text"
                rounded
                size="small"
                aria-label="Hapus"
                :loading="deletingId === data.id"
                @click="onDelete(data)"
              />
            </div>
          </template>
        </Column>

        <template #empty>
          <p class="py-6 text-center text-sm text-slate-500">
            {{ keyword || filterCompany ? 'Tidak ada aplikasi yang cocok.' : 'Belum ada aplikasi.' }}
          </p>
        </template>
      </DataTable>
    </div>

    <Dialog
      v-model:visible="dialogVisible"
      modal
      :header="editing ? 'Ubah Aplikasi' : 'Tambah Aplikasi'"
      :style="{ width: '32rem', maxWidth: '95vw' }"
      :closable="!saving"
      @hide="resetForm"
    >
      <form class="flex flex-col gap-5" novalidate @submit.prevent="onSave">
        <Message v-if="saveError" severity="error" size="small" :closable="false">
          {{ saveError }}
        </Message>

        <div class="flex flex-col gap-2">
          <label for="app-company" class="text-sm font-medium text-slate-800">Company</label>
          <Select
            v-model="form.companyId"
            input-id="app-company"
            :options="companies"
            option-label="name"
            option-value="id"
            placeholder="Pilih company"
            filter
            :disabled="saving || !!editing"
            :invalid="!!errors.companyId"
            fluid
          />
          <Message v-if="errors.companyId" severity="error" size="small" variant="simple">
            {{ errors.companyId }}
          </Message>
          <p v-else-if="editing" class="text-xs text-slate-500">
            Company tidak dapat diubah karena aplikasi mungkin sudah dipakai oleh ticket.
          </p>
        </div>

        <div class="flex flex-col gap-2">
          <label for="app-name" class="text-sm font-medium text-slate-800">Nama Aplikasi</label>
          <InputText
            id="app-name"
            v-model="form.name"
            placeholder="Contoh: HRIS"
            :invalid="!!errors.name"
            :disabled="saving"
            fluid
          />
          <Message v-if="errors.name" severity="error" size="small" variant="simple">
            {{ errors.name }}
          </Message>
        </div>

        <div class="flex flex-col gap-2">
          <label for="app-description" class="text-sm font-medium text-slate-800">
            Deskripsi <span class="font-normal text-slate-400">(opsional)</span>
          </label>
          <Textarea
            id="app-description"
            v-model="form.description"
            rows="3"
            placeholder="Penjelasan singkat tentang aplikasi ini"
            :invalid="!!errors.description"
            :disabled="saving"
            fluid
          />
          <Message v-if="errors.description" severity="error" size="small" variant="simple">
            {{ errors.description }}
          </Message>
        </div>

        <div class="flex justify-end gap-2">
          <Button
            type="button"
            label="Batal"
            severity="secondary"
            variant="text"
            :disabled="saving"
            @click="dialogVisible = false"
          />
          <Button type="submit" label="Simpan" :loading="saving" />
        </div>
      </form>
    </Dialog>
  </div>
</template>