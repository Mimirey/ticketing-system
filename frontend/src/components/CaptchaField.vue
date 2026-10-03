<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { CAPTCHA_EXPIRE_MS, fetchCaptcha } from '@/api/captcha'

const rawAnswer = defineModel<string>('answer', { default: '' })
const captchaId = defineModel<string>('captchaId', { default: '' })

defineProps<{ error?: string }>()

const question = ref('')
const loading = ref(false)
const loadError = ref('')
let timer: ReturnType<typeof setTimeout> | undefined

function handleInput(e: Event) {
  const el = e.target as HTMLInputElement
  const caret = el.selectionStart ?? el.value.length
  const clean = el.value.replace(/\D/g, '')
  const removed = el.value.length - clean.length

  rawAnswer.value = clean
  el.value = clean

  const newCaret = Math.max(0, caret - removed)
  el.setSelectionRange(newCaret, newCaret)
}

async function refresh() {
  clearTimeout(timer)
  loading.value = true
  loadError.value = ''
  rawAnswer.value = ''
  try {
    const challenge = await fetchCaptcha()
    captchaId.value = challenge.captchaId
    question.value = challenge.question
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

    <div class="grid grid-cols-2 gap-2">
      <!-- Soal + tombol refresh di dalam kotak -->
      <div
        class="flex h-9 items-center rounded-md border border-slate-200 bg-slate-50 pr-1 pl-3"
      >
        <span class="flex-1 text-center text-sm font-semibold tracking-wide text-slate-800 select-none">
          <i v-if="loading" class="pi pi-spinner pi-spin text-slate-500"></i>
          <template v-else>{{ question }}</template>
        </span>
        <Button
          type="button"
          icon="pi pi-refresh"
          variant="text"
          rounded
          severity="secondary"
          size="small"
          class="size-7! shrink-0"
          aria-label="Muat ulang captcha"
          :disabled="loading"
          @click="refresh"
        />
      </div>

      <InputText
        id="captcha"
        :model-value="rawAnswer"
        placeholder="Jawaban"
        inputmode="numeric"
        maxlength="3"
        autocomplete="off"
        size="small"
        :invalid="!!error"
        fluid
        @input="handleInput"
      />
    </div>

    <Message v-if="error || loadError" severity="error" size="small" variant="simple">
      {{ error || loadError }}
    </Message>
  </div>
</template>