<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { CAPTCHA_EXPIRE_MS, fetchCaptcha } from '@/api/captcha'

const answer = defineModel<string>('answer', { default: '' })
const captchaId = defineModel<string>('captchaId', { default: '' })

defineProps<{ error?: string }>()

const question = ref('')
const loading = ref(false)
const loadError = ref('')
let timer: ReturnType<typeof setTimeout> | undefined

async function refresh() {
  clearTimeout(timer)
  loading.value = true
  loadError.value = ''
  answer.value = ''
  try {
    const challenge = await fetchCaptcha()
    captchaId.value = challenge.captchaId
    question.value = challenge.question
    // muat ulang sedikit sebelum kedaluwarsa di backend
    timer = setTimeout(refresh, CAPTCHA_EXPIRE_MS - 10_000)
  } catch {
    loadError.value = 'Gagal memuat captcha, coba muat ulang'
  } finally {
    loading.value = false
  }
}

onMounted(refresh)
onBeforeUnmount(() => clearTimeout(timer))

defineExpose({ refresh })
</script>

<template>
  <div class="flex flex-col gap-2">
    <label for="captcha" class="text-sm font-medium text-slate-800">Verifikasi</label>

    <div class="flex items-center gap-2">
      <div
        class="flex h-9 flex-1 items-center justify-center rounded-md border border-slate-200 bg-slate-50 text-sm font-semibold tracking-wide text-slate-800 select-none"
      >
        <i v-if="loading" class="pi pi-spinner pi-spin text-slate-500"></i>
        <span v-else>{{ question }}</span>
      </div>
      <Button
        type="button"
        icon="pi pi-refresh"
        severity="secondary"
        variant="outlined"
        size="small"
        aria-label="Muat ulang captcha"
        :disabled="loading"
        @click="refresh"
      />
    </div>

    <InputText
      id="captcha"
      v-model="answer"
      placeholder="Masukkan hasil perhitungan"
      inputmode="numeric"
      autocomplete="off"
      size="small"
      :invalid="!!error"
      fluid
    />

    <Message v-if="error || loadError" severity="error" size="small" variant="simple">
      {{ error || loadError }}
    </Message>
  </div>
</template>