<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import dayjs from 'dayjs'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { createTelegramLink, fetchMe, type MyProfile, type TelegramLink } from '@/api/users'
import { getErrorMessage } from '@/api/client'
import { ROLE_LABELS, type Role } from '@/constant/permissions'

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
  // Buka tab kosong sekarang (masih dalam klik pengguna), isi alamatnya setelah link jadi
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

// expires_at ditampilkan hanya kalau menyertakan zona waktu, supaya tidak salah jam
const expiresText = computed(() => {
  const s = generated.value?.expires_at
  if (!s || !/(Z|[+-]\d{2}:?\d{2})$/.test(s)) return null
  return dayjs(s).format('HH:mm')
})
</script>

<template>
  <div class="mx-auto max-w-3xl px-6 py-6">
    <h1 class="mb-6 text-xl font-bold text-slate-800">Profil</h1>

    <Message v-if="error" severity="error" size="small" :closable="false" class="mb-4">
      <div class="flex items-center gap-3">
        <span>{{ error }}</span>
        <Button label="Coba lagi" size="small" variant="text" @click="load" />
      </div>
    </Message>

    <div v-if="loading" class="flex flex-col gap-4">
      <div class="h-40 animate-pulse rounded-xl bg-slate-100"></div>
      <div class="h-32 animate-pulse rounded-xl bg-slate-100"></div>
    </div>

    <div v-else-if="profile" class="flex flex-col gap-6">
      <!-- Informasi akun -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="mb-6 flex items-center gap-4">
          <Avatar
            :label="initials"
            shape="circle"
            size="large"
            class="bg-(--p-primary-color)! text-(--p-primary-contrast-color)!"
          />
          <div>
            <p class="text-base font-semibold text-slate-800">{{ profile.name }}</p>
            <p class="text-sm text-slate-500">{{ roleLabel }}</p>
          </div>
        </div>

        <dl class="grid grid-cols-1 gap-x-8 gap-y-4 border-t border-slate-100 pt-5 sm:grid-cols-2">
          <div v-for="r in rows" :key="r.label">
            <dt class="text-xs text-slate-500">{{ r.label }}</dt>
            <dd class="mt-0.5 text-sm font-medium text-slate-800">{{ r.value }}</dd>
          </div>
        </dl>
      </section>

      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex items-start justify-between gap-4">
          <div>
            <h2 class="text-sm font-semibold text-slate-800">Notifikasi Telegram</h2>
            <p class="mt-1 text-sm text-slate-500">
              Hubungkan akunmu ke bot Telegram untuk menerima pengingat ticket.
            </p>
          </div>
          <span
            v-if="profile.telegram_linked !== undefined"
            class="shrink-0 rounded-full px-2.5 py-1 text-xs font-medium"
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
          class="mt-4 rounded-lg bg-(--p-primary-50) p-4 text-sm text-slate-700"
        >
          <p class="font-medium text-slate-800">Link Telegram sudah dibuka di tab baru.</p>
          <ol class="mt-2 list-decimal space-y-1 pl-5">
            <li>Di Telegram, tekan <b>Start</b> pada bot.</li>
            <li>Akunmu otomatis terhubung, tidak perlu mengisi apa pun.</li>
          </ol>
          <p class="mt-2 text-xs text-slate-500">
            Link hanya berlaku sebentar<template v-if="expiresText"> (sampai pukul {{ expiresText }})</template>.
            Kalau tab tidak terbuka atau link kedaluwarsa,
            <a
              :href="generated.telegram_link"
              target="_blank"
              rel="noopener"
              class="font-medium text-(--p-primary-color) underline"
            >buka link ini</a>
            atau buat ulang.
          </p>
        </div>

        <div class="mt-4">
          <Button
            :label="generated ? 'Buat Ulang Link' : 'Hubungkan Telegram'"
            icon="pi pi-telegram"
            :severity="generated ? 'secondary' : undefined"
            :variant="generated ? 'outlined' : undefined"
            size="small"
            :loading="linking"
            @click="connectTelegram"
          />
        </div>
      </section>
    </div>
  </div>
</template>