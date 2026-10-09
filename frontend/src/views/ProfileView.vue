<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import dayjs from 'dayjs'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { createTelegramLink, fetchMe, type MyProfile, type TelegramLink } from '@/api/users'
import { getErrorMessage } from '@/api/client'
import { ROLE_LABELS, type Role } from '@/constant/permissions'
import ChangePasswordForm from '@/components/ChangePasswordForm.vue'

const profile = ref<MyProfile | null>(null)
const loading = ref(true)
const error = ref('')

const linking = ref(false)
const linkError = ref('')
const generated = ref<TelegramLink | null>(null)

async function load() {
  loading.value = true
  error.value = ''
  try {
    profile.value = await fetchMe()
  } catch (e) {
    error.value = getErrorMessage(e, 'Gagal memuat profil')
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function connectTelegram() {
  linkError.value = ''
  const tab = window.open('', '_blank')

  linking.value = true
  try {
    const result = await createTelegramLink()
    generated.value = result
    if (tab) {
      tab.opener = null
      tab.location.href = result.telegram_link
    }
  } catch (e) {
    tab?.close()
    linkError.value = getErrorMessage(e, 'Gagal membuat link Telegram')
  } finally {
    linking.value = false
  }
}

const initials = computed(() =>
  (profile.value?.name ?? '')
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase())
    .join(''),
)

const roleLabel = computed(
  () => ROLE_LABELS[profile.value?.role as Role] ?? profile.value?.role ?? '',
)

const rows = computed(() => {
  const p = profile.value
  if (!p) return []
  return [
    { label: 'Nama', value: p.name },
    ...(p.username ? [{ label: 'Username', value: p.username }] : []),
    { label: 'Email', value: p.email },
    { label: 'Role', value: roleLabel.value },
  ]
})

const expiresText = computed(() => {
  const s = generated.value?.expires_at
  if (!s || !/(Z|[+-]\d{2}:?\d{2})$/.test(s)) return null
  return dayjs(s).format('HH:mm')
})
</script>

<template>
  <!-- Perbesar container dari max-w-3xl menjadi max-w-6xl / 7xl -->
  <div class="mx-auto max-w-6xl px-4 py-8 sm:px-6">
    <h1 class="mb-6 text-2xl font-bold text-slate-800">Profil Saya</h1>

    <!-- Message Error Utama -->
    <Message v-if="error" severity="error" size="small" :closable="false" class="mb-6">
      <div class="flex items-center gap-3">
        <span>{{ error }}</span>
        <Button label="Coba lagi" size="small" variant="text" @click="load" />
      </div>
    </Message>

    <!-- Skeleton Loading -->
    <div v-if="loading" class="grid grid-cols-1 gap-6 lg:grid-cols-12">
      <div class="h-96 animate-pulse rounded-xl bg-slate-100 lg:col-span-5 xl:col-span-4"></div>
      <div class="h-96 animate-pulse rounded-xl bg-slate-100 lg:col-span-7 xl:col-span-8"></div>
    </div>

    <!-- Layout Utama dengan Grid 2 Kolom -->
    <div v-else-if="profile" class="grid grid-cols-1 items-start gap-6 lg:grid-cols-12">
      
      <!-- KOLOM KIRI: Informasi Ringkasan Profil & Telegram -->
      <div class="flex flex-col gap-6 lg:col-span-5 xl:col-span-4">
        
        <!-- Card Profile Header & Details -->
        <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col items-center text-center">
            <Avatar
              :label="initials"
              shape="circle"
              size="xlarge"
              class="mb-3 bg-(--p-primary-color)! text-2xl font-bold text-(--p-primary-contrast-color)!"
            />
            <h2 class="text-lg font-bold text-slate-800">{{ profile.name }}</h2>
            <p class="text-sm font-medium text-slate-500">{{ roleLabel }}</p>
          </div>

          <dl class="mt-6 flex flex-col gap-3 border-t border-slate-100 pt-5">
            <div v-for="r in rows" :key="r.label" class="flex justify-between text-sm">
              <dt class="text-slate-500">{{ r.label }}</dt>
              <dd class="font-medium text-slate-800 text-right">{{ r.value }}</dd>
            </div>
          </dl>
        </section>

        <!-- Card Integrasi Telegram -->
        <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex items-start justify-between gap-2">
            <div>
              <h3 class="text-sm font-semibold text-slate-800">Notifikasi Telegram</h3>
              <p class="mt-1 text-xs text-slate-500">
                Hubungkan akun ke bot Telegram untuk menerima pengingat ticket.
              </p>
            </div>
            <span
              v-if="profile.telegram_linked !== undefined"
              class="shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium"
              :class="
                profile.telegram_linked
                  ? 'bg-emerald-50 text-emerald-700'
                  : 'bg-slate-100 text-slate-600'
              "
            >
              {{ profile.telegram_linked ? 'Terhubung' : 'Belum terhubung' }}
            </span>
          </div>

          <Message v-if="linkError" severity="error" size="small" :closable="false" class="mt-4">
            {{ linkError }}
          </Message>

          <div
            v-if="generated"
            class="mt-4 rounded-lg bg-(--p-primary-50) p-3 text-xs text-slate-700"
          >
            <p class="font-medium text-slate-800">Link Telegram dibuka di tab baru.</p>
            <ol class="mt-1.5 list-decimal space-y-1 pl-4">
              <li>Di Telegram, tekan <b>Start</b>.</li>
              <li>Akun terhubung otomatis.</li>
            </ol>
            <p class="mt-2 text-[11px] text-slate-500">
              Link berlaku sebentar<template v-if="expiresText"> (s/d {{ expiresText }})</template>. Jika bermasalah,
              <a
                :href="generated.telegram_link"
                target="_blank"
                rel="noopener"
                class="font-medium text-(--p-primary-color) underline"
              >buka link ini</a>.
            </p>
          </div>

          <div class="mt-4">
            <Button
              :label="generated ? 'Buat Ulang Link' : 'Hubungkan Telegram'"
              icon="pi pi-telegram"
              :severity="generated ? 'secondary' : undefined"
              :variant="generated ? 'outlined' : undefined"
              size="small"
              class="w-full"
              :loading="linking"
              @click="connectTelegram"
            />
          </div>
        </section>
      </div>

      <!-- KOLOM KANAN: Ganti Password -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-7 xl:col-span-8">
        <div class="border-b border-slate-100 pb-4 mb-5">
          <h2 class="text-base font-semibold text-slate-800">Ganti Password</h2>
          <p class="text-xs text-slate-500 mt-0.5">Perbarui password akun Anda secara berkala untuk menjaga keamanan data.</p>
        </div>

        <div class="max-w-lg">
          <ChangePasswordForm />
        </div>
      </section>

    </div>
  </div>
</template>