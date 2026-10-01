<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import CaptchaField from '@/components/CaptchaField.vue'
import { getErrorMessage } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({ username: '', password: '', captchaId: '', captchaAnswer: '' })
const errors = reactive({ username: '', password: '', captcha: '' })
const submitError = ref('')
const loading = ref(false)

const usernameRef = ref<{ $el: HTMLInputElement } | null>(null)
const captchaRef = ref<InstanceType<typeof CaptchaField> | null>(null)

onMounted(() => {
  usernameRef.value?.$el?.focus()
})

// Hapus pesan error begitu pengguna mengubah isi field
watch(() => form.username, () => (errors.username = ''))
watch(() => form.password, () => (errors.password = ''))
watch(() => form.captchaAnswer, () => (errors.captcha = ''))

function validate(): boolean {
  errors.username = form.username.trim() ? '' : 'Username wajib diisi'
  errors.password = form.password ? '' : 'Password wajib diisi'

  const answer = form.captchaAnswer.trim()
  if (!answer) errors.captcha = 'Jawaban captcha wajib diisi'
  else if (!/^\d+$/.test(answer)) errors.captcha = 'Jawaban harus berupa angka'
  else errors.captcha = ''

  return !errors.username && !errors.password && !errors.captcha
}

async function onSubmit() {
  submitError.value = ''
  if (!validate()) return

  loading.value = true
  try {
    await auth.login({
      identifier: form.username.trim(), // nama field di API backend
      password: form.password,
      captchaId: form.captchaId,
      captchaAnswer: Number(form.captchaAnswer),
    })
    router.push({ name: 'dashboard' })
  } catch (e) {
    submitError.value = getErrorMessage(e, 'Login gagal')
    captchaRef.value?.refresh()
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50 p-4">
    <div class="w-full max-w-md rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
      <div class="mb-8 text-center">
        <div
          class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-(--p-primary-color) text-(--p-primary-contrast-color)"
        >
          <i class="pi pi-ticket text-xl"></i>
        </div>
        <h1 class="text-xl font-bold text-slate-800">Masuk ke Ticketing</h1>
        <p class="mt-1 text-sm text-slate-500">Silakan login untuk melanjutkan</p>
      </div>

      <form class="flex flex-col gap-5" novalidate @submit.prevent="onSubmit">
        <Message v-if="submitError" severity="error" size="small" :closable="false">
          {{ submitError }}
        </Message>

        <div class="flex flex-col gap-2">
          <label for="username" class="text-sm font-medium text-slate-800">Username</label>
          <InputText
            id="username"
            ref="usernameRef"
            v-model="form.username"
            placeholder="Masukkan username"
            autocomplete="username"
            size="small"
            :invalid="!!errors.username"
            fluid
          />
          <Message v-if="errors.username" severity="error" size="small" variant="simple">
            {{ errors.username }}
          </Message>
        </div>

        <div class="flex flex-col gap-2">
          <label for="password" class="text-sm font-medium text-slate-800">Password</label>
          <Password
            v-model="form.password"
            input-id="password"
            placeholder="Masukkan password"
            autocomplete="current-password"
            size="small"
            :feedback="false"
            :invalid="!!errors.password"
            toggle-mask
            fluid
          />
          <Message v-if="errors.password" severity="error" size="small" variant="simple">
            {{ errors.password }}
          </Message>
        </div>

        <CaptchaField
          ref="captchaRef"
          v-model:captcha-id="form.captchaId"
          v-model:answer="form.captchaAnswer"
          :error="errors.captcha"
        />

        <Button type="submit" label="Masuk" size="small" :loading="loading" fluid />
      </form>
    </div>
  </div>
</template>