<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({ username: '', password: '' })
const errors = reactive({ username: '', password: '' })
const submitError = ref('')
const loading = ref(false)

// Ref ke komponen InputText, elemen <input>-nya ada di $el
const usernameRef = ref<{ $el: HTMLInputElement } | null>(null)

onMounted(() => {
  usernameRef.value?.$el.focus()
})

function validate(): boolean {
  errors.username = form.username.trim() ? '' : 'Username wajib diisi'
  errors.password = form.password ? '' : 'Password wajib diisi'
  return !errors.username && !errors.password
}

async function onSubmit() {
  submitError.value = ''
  if (!validate()) return

  loading.value = true
  try {
    await auth.login(form.username.trim(), form.password)
    router.push({ name: 'dashboard' })
  } catch (e) {
    submitError.value = e instanceof Error ? e.message : 'Terjadi kesalahan'
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

        <Button type="submit" label="Masuk" size="small" :loading="loading" fluid />
      </form>
    </div>
  </div>
</template>