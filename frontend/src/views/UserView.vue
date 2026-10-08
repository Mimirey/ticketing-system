<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Select from 'primevue/select'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { createUser, deleteUser, fetchAllUsers, type UserAccount } from '@/api/users'
import { getErrorMessage, getFieldErrors } from '@/api/client'
import { ROLE_IDS, ROLE_LABELS, ROLE_OPTIONS, type Role } from '@/constant/permissions'
import { useAuthStore } from '@/stores/auth'

const PAGE_SIZE = 10
const MIN_PASSWORD = 8

const auth = useAuthStore()
const toast = useToast()
const confirm = useConfirm()

const users = ref<UserAccount[]>([])
const loading = ref(true)
const error = ref('')
const keyword = ref('')
const filterRole = ref<Role | null>(null)
const visibleCount = ref(PAGE_SIZE)

const dialogVisible = ref(false)
const saving = ref(false)
const saveError = ref('')
const deletingId = ref<number | null>(null)

const form = reactive({
  name: '',
  username: '',
  email: '',
  password: '',
  role: null as Role | null,
})

const errors = reactive({
  name: '',
  username: '',
  email: '',
  password: '',
  role: '',
})

const roleLabel = (role: string) => ROLE_LABELS[role as Role] ?? role
const isSelf = (user: UserAccount) => user.id === auth.user?.id

const initials = (name: string) =>
  name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase())
    .join('')

const filtered = computed(() => {
  const k = keyword.value.trim().toLowerCase()

  return users.value
    .filter((u) => !filterRole.value || u.role === filterRole.value)
    .filter(
      (u) =>
        !k ||
        u.name.toLowerCase().includes(k) ||
        (u.username ?? '').toLowerCase().includes(k) ||
        u.email.toLowerCase().includes(k),
    )
    .sort((a, b) => a.name.localeCompare(b.name, 'id'))
})

const shown = computed(() => filtered.value.slice(0, visibleCount.value))
const remaining = computed(() => Math.max(0, filtered.value.length - visibleCount.value))

watch([keyword, filterRole], () => {
  visibleCount.value = PAGE_SIZE
})

for (const key of Object.keys(errors) as (keyof typeof errors)[]) {
  watch(
    () => form[key],
    () => (errors[key] = ''),
  )
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    users.value = await fetchAllUsers()
  } catch (e) {
    error.value = getErrorMessage(e, 'Gagal memuat daftar user')
  } finally {
    loading.value = false
  }
}

onMounted(load)

function resetForm() {
  form.name = ''
  form.username = ''
  form.email = ''
  form.password = ''
  form.role = null
  for (const key of Object.keys(errors) as (keyof typeof errors)[]) errors[key] = ''
  saveError.value = ''
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function validate(): boolean {
  const name = form.name.trim()
  const username = form.username.trim()
  const email = form.email.trim()

  errors.name = name ? '' : 'Nama wajib diisi'

  if (!username) errors.username = 'Username wajib diisi'
  else if (!/^[A-Za-z0-9._-]{3,50}$/.test(username))
    errors.username = 'Username 3 sampai 50 karakter, hanya huruf, angka, titik, strip, dan garis bawah'
  else if (users.value.some((u) => (u.username ?? '').toLowerCase() === username.toLowerCase()))
    errors.username = 'Username sudah dipakai'
  else errors.username = ''

  if (!email) errors.email = 'Email wajib diisi'
  else if (!/^\S+@\S+\.\S+$/.test(email)) errors.email = 'Format email tidak valid'
  else if (users.value.some((u) => u.email.toLowerCase() === email.toLowerCase()))
    errors.email = 'Email sudah dipakai'
  else errors.email = ''

  if (!form.password) errors.password = 'Password wajib diisi'
  else if (form.password.length < MIN_PASSWORD)
    errors.password = `Password minimal ${MIN_PASSWORD} karakter`
  else errors.password = ''

  errors.role = form.role ? '' : 'Role wajib dipilih'

  return Object.values(errors).every((m) => !m)
}

async function onSave() {
  saveError.value = ''
  if (!validate()) return

  saving.value = true
  try {
    await createUser({
      username: form.username.trim(),
      name: form.name.trim(),
      email: form.email.trim(),
      password: form.password,
      role_id: ROLE_IDS[form.role!],
      telegram_chat_id: null,
    })

    toast.add({ severity: 'success', summary: 'User ditambahkan', life: 3000 })
    dialogVisible.value = false
    await load()
  } catch (e) {
    const fields = getFieldErrors(e)
    const map: Record<string, keyof typeof errors> = {
      name: 'name',
      username: 'username',
      email: 'email',
      password: 'password',
      role_id: 'role',
    }

    let applied = false
    for (const [key, message] of Object.entries(fields)) {
      const target = map[key]
      if (target) {
        errors[target] = message
        applied = true
      }
    }

    if (!applied) saveError.value = getErrorMessage(e, 'Gagal menambahkan user')
  } finally {
    saving.value = false
  }
}

function onDelete(user: UserAccount) {
  if (isSelf(user)) return

  confirm.require({
    header: 'Hapus user?',
    message: `Akun "${user.name}" akan dinonaktifkan dan tidak bisa login lagi. Ticket yang pernah dibuat atau ditugaskan kepadanya tetap ada.`,
    icon: 'pi pi-exclamation-triangle',
    rejectProps: { label: 'Batal', severity: 'secondary', variant: 'text', size: 'small' },
    acceptProps: { label: 'Hapus', severity: 'danger', size: 'small' },
    accept: async () => {
      deletingId.value = user.id
      try {
        await deleteUser(user.id)
        toast.add({ severity: 'success', summary: 'User dihapus', life: 3000 })
        await load()
      } catch (e) {
        toast.add({
          severity: 'error',
          summary: 'Gagal menghapus',
          detail: getErrorMessage(e),
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
  <div class="mx-auto max-w-5xl px-4 py-6 sm:px-6">
    <div class="mb-6 flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-xl font-bold text-slate-800">User</h1>
        <p class="mt-1 text-sm text-slate-500">Kelola akun yang bisa masuk ke sistem</p>
      </div>

      <Button label="Tambah User" icon="pi pi-plus" size="small" @click="openCreate" />
    </div>

    <div class="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center">
      <IconField class="w-full sm:w-72">
        <InputIcon class="pi pi-search" />
        <InputText v-model="keyword" placeholder="Cari nama, username, atau email" size="small" fluid />
      </IconField>

      <div class="w-full sm:w-44">
        <Select
          v-model="filterRole"
          :options="ROLE_OPTIONS"
          option-label="label"
          option-value="value"
          placeholder="Semua Role"
          show-clear
          size="small"
          fluid
        />
      </div>
    </div>

    <Message v-if="error" severity="error" size="small" :closable="false" class="mb-4">
      <div class="flex items-center gap-3">
        <span>{{ error }}</span>
        <Button label="Coba lagi" size="small" variant="text" @click="load" />
      </div>
    </Message>

    <div class="hidden overflow-hidden rounded-xl border border-slate-200 bg-white md:block">
      <DataTable
        :value="filtered"
        :loading="loading"
        size="small"
        data-key="id"
        :paginator="filtered.length > PAGE_SIZE"
        :rows="PAGE_SIZE"
        class="text-sm! [&_th]:py-2.5! [&_th]:text-xs! [&_th]:font-semibold! [&_th]:text-slate-500! [&_td]:py-2!"
      >
        <Column header="Nama">
          <template #body="{ data }">
            <span class="font-medium whitespace-nowrap text-slate-800">{{ data.name }}</span>
            <span v-if="isSelf(data)" class="ml-2 text-xs whitespace-nowrap text-slate-400">(Kamu)</span>
          </template>
        </Column>

        <Column header="Username">
          <template #body="{ data }">
            <span v-if="data.username">{{ data.username }}</span>
            <span v-else class="text-slate-400">-</span>
          </template>
        </Column>

        <Column field="email" header="Email" />

        <Column header="Role">
          <template #body="{ data }">
            <span class="text-sm whitespace-nowrap text-slate-600">{{ roleLabel(data.role) }}</span>
          </template>
        </Column>

        <Column header="Aksi" style="width: 6rem">
          <template #body="{ data }">
            <Button
              icon="pi pi-trash"
              severity="danger"
              variant="text"
              rounded
              size="small"
              :aria-label="isSelf(data) ? 'Akun sendiri tidak bisa dihapus' : 'Hapus'"
              :title="isSelf(data) ? 'Akun sendiri tidak bisa dihapus' : 'Hapus user'"
              :disabled="isSelf(data)"
              :loading="deletingId === data.id"
              @click="onDelete(data)"
            />
          </template>
        </Column>

        <template #empty>
          <p class="py-6 text-center text-sm text-slate-500">
            {{ keyword || filterRole ? 'Tidak ada user yang cocok.' : 'Belum ada user.' }}
          </p>
        </template>
      </DataTable>
    </div>

    <div class="md:hidden">
      <div v-if="loading" class="flex flex-col gap-3">
        <div v-for="n in 4" :key="n" class="h-24 animate-pulse rounded-xl bg-slate-100"></div>
      </div>

      <div
        v-else-if="!filtered.length"
        class="flex flex-col items-center gap-2 rounded-xl border border-slate-200 bg-white py-10 text-center"
      >
        <i class="pi pi-users text-3xl text-slate-300"></i>
        <p class="text-sm text-slate-500">
          {{ keyword || filterRole ? 'Tidak ada user yang cocok.' : 'Belum ada user.' }}
        </p>
      </div>

      <template v-else>
        <ul class="flex flex-col gap-3">
          <li
            v-for="u in shown"
            :key="u.id"
            class="flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-4"
          >
            <span
              class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-slate-100 text-sm font-semibold text-slate-600"
              aria-hidden="true"
            >
              {{ initials(u.name) }}
            </span>

            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-semibold text-slate-800">
                {{ u.name }}
                <span v-if="isSelf(u)" class="ml-1 text-xs font-normal text-slate-400">(Kamu)</span>
              </p>
              <p v-if="u.username" class="truncate text-xs text-slate-500">@{{ u.username }}</p>
              <p class="truncate text-xs text-slate-500">{{ u.email }}</p>
              <span
                class="mt-2 inline-flex items-center rounded-full border border-slate-200 bg-white px-2.5 py-0.5 text-xs font-medium text-slate-700"
              >
                {{ roleLabel(u.role) }}
              </span>
            </div>

            <Button
              icon="pi pi-trash"
              severity="danger"
              variant="text"
              rounded
              size="small"
              :aria-label="isSelf(u) ? 'Akun sendiri tidak bisa dihapus' : 'Hapus'"
              :disabled="isSelf(u)"
              :loading="deletingId === u.id"
              @click="onDelete(u)"
            />
          </li>
        </ul>

        <div v-if="remaining > 0" class="mt-4">
          <Button
            :label="`Tampilkan lebih banyak (${remaining})`"
            severity="secondary"
            variant="outlined"
            size="small"
            fluid
            @click="visibleCount += PAGE_SIZE"
          />
        </div>
      </template>
    </div>

    <Dialog
      v-model:visible="dialogVisible"
      modal
      header="Tambah User"
      :style="{ width: '32rem', maxWidth: '95vw' }"
      :closable="!saving"
      @hide="resetForm"
    >
      <form class="flex flex-col gap-5" novalidate @submit.prevent="onSave">
        <Message v-if="saveError" severity="error" size="small" :closable="false">
          {{ saveError }}
        </Message>

        <div class="flex flex-col gap-2">
          <label for="user-name" class="text-sm font-medium text-slate-800">Nama Lengkap</label>
          <InputText
            id="user-name"
            v-model="form.name"
            placeholder="Contoh: Budi Santoso"
            autocomplete="off"
            :invalid="!!errors.name"
            :disabled="saving"
            fluid
          />
          <Message v-if="errors.name" severity="error" size="small" variant="simple">
            {{ errors.name }}
          </Message>
        </div>

        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <div class="flex flex-col gap-2">
            <label for="user-username" class="text-sm font-medium text-slate-800">Username</label>
            <InputText
              id="user-username"
              v-model="form.username"
              placeholder="budi.santoso"
              autocomplete="off"
              :invalid="!!errors.username"
              :disabled="saving"
              fluid
            />
            <Message v-if="errors.username" severity="error" size="small" variant="simple">
              {{ errors.username }}
            </Message>
          </div>

          <div class="flex flex-col gap-2">
            <label for="user-role" class="text-sm font-medium text-slate-800">Role</label>
            <Select
              v-model="form.role"
              input-id="user-role"
              :options="ROLE_OPTIONS"
              option-label="label"
              option-value="value"
              placeholder="Pilih role"
              :invalid="!!errors.role"
              :disabled="saving"
              fluid
            />
            <Message v-if="errors.role" severity="error" size="small" variant="simple">
              {{ errors.role }}
            </Message>
          </div>
        </div>

        <div class="flex flex-col gap-2">
          <label for="user-email" class="text-sm font-medium text-slate-800">Email</label>
          <InputText
            id="user-email"
            v-model="form.email"
            type="email"
            placeholder="budi@perusahaan.com"
            autocomplete="off"
            :invalid="!!errors.email"
            :disabled="saving"
            fluid
          />
          <Message v-if="errors.email" severity="error" size="small" variant="simple">
            {{ errors.email }}
          </Message>
        </div>

        <div class="flex flex-col gap-2">
          <label for="user-password" class="text-sm font-medium text-slate-800">Password</label>
          <Password
            v-model="form.password"
            input-id="user-password"
            placeholder="Minimal 8 karakter"
            autocomplete="new-password"
            :feedback="false"
            toggle-mask
            :invalid="!!errors.password"
            :disabled="saving"
            fluid
          />
          <Message v-if="errors.password" severity="error" size="small" variant="simple">
            {{ errors.password }}
          </Message>
          <p v-else class="text-xs text-slate-500">
            Sampaikan password ini ke pemilik akun. Setelah disimpan, password tidak bisa dilihat lagi.
          </p>
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