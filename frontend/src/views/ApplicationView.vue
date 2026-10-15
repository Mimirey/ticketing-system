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
import MultiSelect from 'primevue/multiselect'
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
  companyIds: [] as number[],
  name: '',
  description: '',
})

const errors = reactive({
  companyIds: '',
  name: '',
  description: '',
})

const filtered = computed(() => {
  const k = keyword.value.trim().toLowerCase()

  return applications.value
    .filter(
      (a) => !filterCompany.value || a.companies.some((c) => c.id === filterCompany.value),
    )
    .filter(
      (a) =>
        !k ||
        a.name.toLowerCase().includes(k) ||
        (a.description ?? '').toLowerCase().includes(k),
    )
    .sort((a, b) => a.name.localeCompare(b.name, 'id'))
})

watch(
  () => form.companyIds.length,
  () => (errors.companyIds = ''),
)
watch(
  () => form.name,
  () => (errors.name = ''),
)
watch(
  () => form.description,
  () => (errors.description = ''),
)

function companySummary(list: Company[]) {
  const names = list.map((c) => c.name)
  return names.length <= 2
    ? names.join(', ')
    : `${names.slice(0, 2).join(', ')} +${names.length - 2}`
}

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
  form.companyIds = []
  form.name = ''
  form.description = ''
  errors.companyIds = ''
  errors.name = ''
  errors.description = ''
  saveError.value = ''
}

function openCreate() {
  resetForm()
  if (filterCompany.value) form.companyIds = [filterCompany.value]
  dialogVisible.value = true
}

function openEdit(app: Application) {
  resetForm()
  editing.value = app
  form.companyIds = app.companies.map((c) => c.id)
  form.name = app.name
  form.description = app.description ?? ''
  dialogVisible.value = true
}

function validate(): boolean {
  const name = form.name.trim()

  errors.companyIds = form.companyIds.length ? '' : 'Pilih minimal satu company'

  if (!name) {
    errors.name = 'Nama aplikasi wajib diisi'
  } else if (
    applications.value.some(
      (a) => a.id !== editing.value?.id && a.name.trim().toLowerCase() === name.toLowerCase(),
    )
  ) {
    errors.name = 'Nama aplikasi sudah terdaftar'
  } else {
    errors.name = ''
  }

  return !errors.companyIds && !errors.name
}

async function onSave() {
  saveError.value = ''
  if (!validate()) return

  saving.value = true
  try {
    const payload = {
      company_ids: form.companyIds,
      name: form.name.trim(),
      description: form.description.trim() || null,
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

    if (fields.company_ids) {
      errors.companyIds = fields.company_ids
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

    if (!applied) {
      const message = getErrorMessage(e, 'Gagal menyimpan aplikasi')
      if (/nama/i.test(message)) errors.name = message
      else if (/company/i.test(message)) errors.companyIds = message
      else saveError.value = message
    }
  } finally {
    saving.value = false
  }
}

function onDelete(app: Application) {
  confirm.require({
    header: 'Hapus aplikasi?',
    message: `"${app.name}" akan dihapus permanen beserta relasinya dengan ${app.companies.length} company.`,
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
        toast.add({
          severity: 'error',
          summary: 'Gagal menghapus',
          detail:
            getErrorStatus(e) === 500
              ? 'Aplikasi tidak bisa dihapus saat ini karena ada kendala di server.'
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
          Kelola aplikasi dan company yang memakainya
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
          <template #body="{ data }">
            <span
              v-if="data.companies.length"
              class="text-slate-700"
              :title="data.companies.map((c: Company) => c.name).join(', ')"
            >
              {{ companySummary(data.companies) }}
            </span>
            <span v-else class="text-slate-400">-</span>
          </template>
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
          <label for="app-companies" class="text-sm font-medium text-slate-800">Company</label>
          <MultiSelect
            v-model="form.companyIds"
            input-id="app-companies"
            :options="companies"
            option-label="name"
            option-value="id"
            placeholder="Pilih company"
            filter
            filter-placeholder="Cari company"
            :max-selected-labels="2"
            selected-items-label="{0} company dipilih"
            :invalid="!!errors.companyIds"
            :disabled="saving"
            fluid
          />
          <Message v-if="errors.companyIds" severity="error" size="small" variant="simple">
            {{ errors.companyIds }}
          </Message>
          <p v-else class="text-xs text-slate-500">
            Satu aplikasi bisa dipakai oleh beberapa company. Pilih minimal satu.
          </p>
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