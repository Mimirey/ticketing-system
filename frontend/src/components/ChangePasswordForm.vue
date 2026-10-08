<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { changePassword } from '@/api/users'
import { getErrorMessage, getErrorStatus, getFieldErrors } from '@/api/client'
import { validatePassword } from '@/utils/password'
import PasswordRules from '@/components/PasswordRules.vue'

const emit = defineEmits<{
  done: []
}>()

const toast = useToast()

const form = reactive({
  current: '',
  next: '',
  confirm: '',
})

const errors = reactive({
  current: '',
  next: '',
  confirm: '',
})

const saving = ref(false)
const submitError = ref('')

for (const key of Object.keys(errors) as (keyof typeof errors)[]) {
  watch(
    () => form[key],
    () => (errors[key] = ''),
  )
}

function resetForm() {
  form.current = ''
  form.next = ''
  form.confirm = ''
  for (const key of Object.keys(errors) as (keyof typeof errors)[]) errors[key] = ''
  submitError.value = ''
}

function validate(): boolean {
  errors.current = form.current ? '' : 'Password saat ini wajib diisi'

  const nextError = form.next ? validatePassword(form.next) : 'Password baru wajib diisi'
  errors.next =
    nextError ||
    (form.next === form.current ? 'Password baru harus berbeda dari password saat ini' : '')

  if (!form.confirm) errors.confirm = 'Konfirmasi password wajib diisi'
  else if (form.confirm !== form.next) errors.confirm = 'Konfirmasi password tidak cocok'
  else errors.confirm = ''

  return Object.values(errors).every((m) => !m)
}

async function onSubmit() {
  submitError.value = ''
  if (!validate()) return

  saving.value = true
  try {
    await changePassword({
      current_password: form.current,
      new_password: form.next,
    })

    toast.add({ severity: 'success', summary: 'Password berhasil diubah', life: 3000 })
    resetForm()
    emit('done')
  } catch (e) {
    const fields = getFieldErrors(e)

    if (fields.current_password) errors.current = fields.current_password
    if (fields.new_password) errors.next = fields.new_password

    if (fields.current_password || fields.new_password) return

    if (getErrorStatus(e) === 400) {
      errors.current = getErrorMessage(e, 'Password saat ini salah')
      return
    }

    submitError.value = getErrorMessage(e, 'Gagal mengubah password')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <form class="flex flex-col gap-4" novalidate @submit.prevent="onSubmit">
    <Message v-if="submitError" severity="error" size="small" :closable="false">
      {{ submitError }}
    </Message>

    <div class="flex flex-col gap-2">
      <label for="current-password" class="text-sm font-medium text-slate-800">Password Saat Ini</label>
      <Password
        v-model="form.current"
        input-id="current-password"
        size="small"
        autocomplete="current-password"
        :feedback="false"
        toggle-mask
        :invalid="!!errors.current"
        :disabled="saving"
        fluid
      />
      <Message v-if="errors.current" severity="error" size="small" variant="simple">
        {{ errors.current }}
      </Message>
    </div>

    <div class="flex flex-col gap-2">
      <label for="new-password" class="text-sm font-medium text-slate-800">Password Baru</label>
      <Password
        v-model="form.next"
        input-id="new-password"
        size="small"
        autocomplete="new-password"
        :feedback="false"
        toggle-mask
        :invalid="!!errors.next"
        :disabled="saving"
        fluid
      />
      <PasswordRules :password="form.next" />
      <Message v-if="errors.next" severity="error" size="small" variant="simple">
        {{ errors.next }}
      </Message>
    </div>

    <div class="flex flex-col gap-2">
      <label for="confirm-password" class="text-sm font-medium text-slate-800">Konfirmasi Password Baru</label>
      <Password
        v-model="form.confirm"
        input-id="confirm-password"
        size="small"
        autocomplete="new-password"
        :feedback="false"
        toggle-mask
        :invalid="!!errors.confirm"
        :disabled="saving"
        fluid
      />
      <Message v-if="errors.confirm" severity="error" size="small" variant="simple">
        {{ errors.confirm }}
      </Message>
    </div>

    <div class="flex pt-1">
      <Button type="submit" label="Ubah Password" size="small" :loading="saving" />
    </div>
  </form>
</template>