<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import CaptchaField from '@/components/CaptchaField.vue'
import { getErrorMessage } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import apg from '@/assets/apg.svg'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const expired = route.query.expired === '1'

const form = reactive({ username: '', password: '', captchaId: '', captchaAnswer: '' })
const errors = reactive({ username: '', password: '', captcha: '' })
const submitError = ref('')
const loading = ref(false)

const usernameRef = ref<{ $el: HTMLInputElement } | null>(null)
const captchaRef = ref<InstanceType<typeof CaptchaField> | null>(null)

onMounted(() => {
  usernameRef.value?.$el?.focus()
})

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

function redirectTarget() {
  const r = route.query.redirect
  if (typeof r === 'string' && r.startsWith('/') && !r.startsWith('//')) return r
  return { name: 'tickets' }
}

async function onSubmit() {
  submitError.value = ''
  if (!validate()) return

  loading.value = true
  try {
    await auth.login({
      identifier: form.username.trim(), 
      password: form.password,
      captchaId: form.captchaId,
      captchaAnswer: Number(form.captchaAnswer),
    })
    router.push(redirectTarget())
  } catch (e) {
    submitError.value = getErrorMessage(e, 'Login gagal')
    captchaRef.value?.refresh()
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div
    class="relative flex min-h-screen items-center justify-center overflow-hidden bg-linear-to-br from-slate-50 via-slate-50 to-indigo-100/60 p-4"
  >
    <div aria-hidden="true" class="pointer-events-none absolute inset-0">
    <div
      class="absolute inset-0"
      style="
        background-image: radial-gradient(circle, rgb(36 53 160 / 0.22) 1.5px, transparent 1.5px);
        background-size: 26px 26px;
        mask-image: radial-gradient(ellipse at center, transparent 25%, black 85%);
        -webkit-mask-image: radial-gradient(ellipse at center, transparent 25%, black 85%);
      "
    ></div>
      <div class="absolute -top-32 -left-32 h-[28rem] w-[28rem] rounded-full bg-(--p-primary-color)/25 blur-3xl"></div>
      <div class="absolute -right-32 -bottom-32 h-[28rem] w-[28rem] rounded-full bg-(--p-primary-color)/25 blur-3xl"></div>
    </div>

    <div class="relative w-full max-w-md">
      <div class="rounded-xl border border-slate-200 bg-white p-8 shadow-lg shadow-slate-200/60">
        <div class="mb-8 flex flex-col items-center text-center">
          <img :src="apg" alt="Logo perusahaan" class="mb-5 h-18 w-auto object-contain" />
          <h1 class="text-xl font-bold text-slate-800">Selamat Datang</h1>
          <p class="mt-1 text-sm text-slate-500">Silakan login untuk melanjutkan</p>
        </div>

        <form class="flex flex-col gap-6" novalidate @submit.prevent="onSubmit">
          <Message
            v-if="expired && !submitError"
            severity="warn"
            size="small"
            :closable="false"
          >
            Sesi kamu telah berakhir, silakan login lagi.
          </Message>

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
  </div>
</template>