<script setup lang="ts">
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Message from 'primevue/message'

import type { Role } from '@/constant/permissions'

interface UserForm {
  name: string
  username: string
  email: string
  role: Role | null
}

interface FormErrors {
  name?: string
  username?: string
  email?: string
  role?: string
}

interface RoleOption {
  label: string
  value: string
}

const props = defineProps<{
  visible: boolean
  saving: boolean
  saveError: string
  form: UserForm
  errors: FormErrors
  roleOptions: RoleOption[]
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  save: []
  reset: []
}>()

function close() {
  if (props.saving) return
  emit('update:visible', false)
}

function handleHide() {
  emit('reset')
}
</script>

<template>
  <Dialog
    :visible="visible"
    modal
    header="Tambah User"
    :style="{ width: '32rem', maxWidth: '95vw' }"
    :closable="!saving"
    @update:visible="emit('update:visible', $event)"
    @hide="handleHide"
  >
    <form
      class="flex flex-col gap-5"
      novalidate
      @submit.prevent="emit('save')"
    >
      <Message
        v-if="saveError"
        severity="error"
        size="small"
        :closable="false"
      >
        {{ saveError }}
      </Message>

      <Message
        severity="info"
        size="small"
        icon="pi pi-info-circle"
        :closable="false"
      >
        Password awal memakai password default "Admin123". User bisa menggantinya
        sendiri setelah login.
      </Message>

      <!-- Nama -->
      <div class="flex flex-col gap-2">
        <label
          for="user-name"
          class="text-sm font-medium text-slate-800"
        >
          Nama Lengkap
        </label>

        <InputText
          id="user-name"
          v-model="form.name"
          placeholder="Contoh: Budi Santoso"
          autocomplete="off"
          :invalid="!!errors.name"
          :disabled="saving"
          fluid
        />

        <Message
          v-if="errors.name"
          severity="error"
          size="small"
          variant="simple"
        >
          {{ errors.name }}
        </Message>
      </div>

      <!-- Username + Role -->
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <!-- Username -->
        <div class="flex flex-col gap-2">
          <label
            for="user-username"
            class="text-sm font-medium text-slate-800"
          >
            Username
          </label>

          <InputText
            id="user-username"
            v-model="form.username"
            placeholder="budi.santoso"
            autocomplete="off"
            :invalid="!!errors.username"
            :disabled="saving"
            fluid
          />

          <Message
            v-if="errors.username"
            severity="error"
            size="small"
            variant="simple"
          >
            {{ errors.username }}
          </Message>
        </div>

        <!-- Role -->
        <div class="flex flex-col gap-2">
          <label
            for="user-role"
            class="text-sm font-medium text-slate-800"
          >
            Role
          </label>

          <Select
            v-model="form.role"
            input-id="user-role"
            :options="roleOptions"
            option-label="label"
            option-value="value"
            placeholder="Pilih role"
            :invalid="!!errors.role"
            :disabled="saving"
            fluid
          />

          <Message
            v-if="errors.role"
            severity="error"
            size="small"
            variant="simple"
          >
            {{ errors.role }}
          </Message>
        </div>
      </div>

      <!-- Email -->
      <div class="flex flex-col gap-2">
        <label
          for="user-email"
          class="text-sm font-medium text-slate-800"
        >
          Email
        </label>

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

        <Message
          v-if="errors.email"
          severity="error"
          size="small"
          variant="simple"
        >
          {{ errors.email }}
        </Message>
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-2">
        <Button
          type="button"
          label="Batal"
          severity="secondary"
          variant="text"
          :disabled="saving"
          @click="close"
        />

        <Button
          type="submit"
          label="Simpan"
          :loading="saving"
        />
      </div>
    </form>
  </Dialog>
</template>