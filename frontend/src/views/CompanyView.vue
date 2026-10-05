<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Button from 'primevue/button'
import Message from 'primevue/message'
import {
  createCompany,
  deleteCompany,
  fetchApplications,
  fetchCompanies,
  updateCompany,
  type Company,
} from '@/api/master'
import { getErrorMessage, getErrorStatus, getFieldErrors } from '@/api/client'

const PAGE_SIZE = 10

const toast = useToast()
const confirm = useConfirm()

const companies = ref<Company[]>([])
const loading = ref(true)
const error = ref('')
const keyword = ref('')

const dialogVisible = ref(false)
const editing = ref<Company | null>(null)
const name = ref('')
const nameError = ref('')
const saveError = ref('')
const saving = ref(false)
const deletingId = ref<number | null>(null)

const filtered = computed(() => {
  const k = keyword.value.trim().toLowerCase()
  const list = k
    ? companies.value.filter((c) => c.name.toLowerCase().includes(k))
    : companies.value
  return [...list].sort((a, b) => a.name.localeCompare(b.name, 'id'))
})

watch(name, () => {
  nameError.value = ''
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    companies.value = await fetchCompanies()
  } catch (e) {
    error.value = getErrorMessage(e, 'Gagal memuat daftar company')
  } finally {
    loading.value = false
  }
}

onMounted(load)

function resetForm() {
  editing.value = null
  name.value = ''
  nameError.value = ''
  saveError.value = ''
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(company: Company) {
  resetForm()
  editing.value = company
  name.value = company.name
  dialogVisible.value = true
}

function validate(): boolean {
  const value = name.value.trim()

  if (!value) {
    nameError.value = 'Nama company wajib diisi'
    return false
  }

  const duplicate = companies.value.some(
    (c) => c.id !== editing.value?.id && c.name.trim().toLowerCase() === value.toLowerCase(),
  )
  if (duplicate) {
    nameError.value = 'Nama company sudah ada'
    return false
  }

  nameError.value = ''
  return true
}

async function onSave() {
  saveError.value = ''
  if (!validate()) return

  saving.value = true
  try {
    const payload = { name: name.value.trim() }
    const isEdit = !!editing.value

    if (editing.value) await updateCompany(editing.value.id, payload)
    else await createCompany(payload)

    toast.add({
      severity: 'success',
      summary: isEdit ? 'Company diperbarui' : 'Company ditambahkan',
      life: 3000,
    })
    dialogVisible.value = false
    await load()
  } catch (e) {
    const fields = getFieldErrors(e)
    if (fields.name) nameError.value = fields.name
    else saveError.value = getErrorMessage(e, 'Gagal menyimpan company')
  } finally {
    saving.value = false
  }
}

async function onDelete(company: Company) {
  let appCount = 0
  try {
    appCount = (await fetchApplications(company.id)).length
  } catch {
    appCount = 0
  }

  const extra = appCount ? ` ${appCount} aplikasi di dalamnya juga akan ikut terhapus.` : ''

  confirm.require({
    header: 'Hapus company?',
    message: `"${company.name}" akan dihapus permanen.${extra}`,
    icon: 'pi pi-exclamation-triangle',
    rejectProps: { label: 'Batal', severity: 'secondary', variant: 'text', size: 'small' },
    acceptProps: { label: 'Hapus', severity: 'danger', size: 'small' },
    accept: async () => {
      deletingId.value = company.id
      try {
        await deleteCompany(company.id)
        toast.add({ severity: 'success', summary: 'Company dihapus', life: 3000 })
        await load()
      } catch (e) {
        const status = getErrorStatus(e)
        toast.add({
          severity: 'error',
          summary: 'Gagal menghapus',
          detail:
            status === 500 || status === 409
              ? 'Company tidak bisa dihapus karena masih dipakai oleh ticket.'
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
  <div class="mx-auto max-w-4xl px-6 py-6">
    <div class="mb-6 flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-xl font-bold text-slate-800">Company</h1>
        <p class="mt-1 text-sm text-slate-500">
          Kelola daftar company yang bisa dipilih saat membuat ticket
        </p>
      </div>

      <Button label="Tambah Company" icon="pi pi-plus" size="small" @click="openCreate" />
    </div>

    <div class="mb-4">
      <IconField class="w-full sm:w-72">
        <InputIcon class="pi pi-search" />
        <InputText v-model="keyword" placeholder="Cari company" size="small" fluid />
      </IconField>
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
        <Column field="name" header="Nama Company" />

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
            {{ keyword ? 'Tidak ada company yang cocok.' : 'Belum ada company.' }}
          </p>
        </template>
      </DataTable>
    </div>

    <Dialog
      v-model:visible="dialogVisible"
      modal
      :header="editing ? 'Ubah Company' : 'Tambah Company'"
      :style="{ width: '28rem', maxWidth: '95vw' }"
      :closable="!saving"
      @hide="resetForm"
    >
      <form class="flex flex-col gap-5" novalidate @submit.prevent="onSave">
        <Message v-if="saveError" severity="error" size="small" :closable="false">
          {{ saveError }}
        </Message>

        <div class="flex flex-col gap-2">
          <label for="company-name" class="text-sm font-medium text-slate-800">Nama Company</label>
          <InputText
            id="company-name"
            v-model="name"
            placeholder="Contoh: Amazink People Group"
            :invalid="!!nameError"
            :disabled="saving"
            autofocus
            fluid
          />
          <Message v-if="nameError" severity="error" size="small" variant="simple">
            {{ nameError }}
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