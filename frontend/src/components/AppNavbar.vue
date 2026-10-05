<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import Drawer from 'primevue/drawer'
import Menu from 'primevue/menu'
import { useAuthStore } from '@/stores/auth'
import { ROLE_LABELS, type Permission, type Role } from '@/constant/permissions'
import apg from '@/assets/apg.svg'
import NotificationBell from '@/components/NotificationBell.vue'

interface NavItem {
  label: string
  to: string
  icon: string
  permission?: Permission // kosong = semua role
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Tickets', to: '/tickets', icon: 'pi pi-ticket' },
  { label: 'Dashboard', to: '/dashboard', icon: 'pi pi-chart-bar' },
  { label: 'Activity Log', to: '/activity-log', icon: 'pi pi-history', permission: 'activity-log:view' },
  { label: 'Company', to: '/companies', icon: 'pi pi-building', permission: 'master:manage' },
  { label: 'Aplikasi', to: '/applications', icon: 'pi pi-box', permission: 'master:manage' },
]

const router = useRouter()
const auth = useAuthStore()

const visibleItems = computed(() =>
  NAV_ITEMS.filter((i) => !i.permission || auth.can(i.permission)),
)

const roleLabel = computed(() => ROLE_LABELS[auth.user?.role as Role] ?? auth.user?.role ?? '')

const initials = computed(() => {
  const parts = (auth.user?.name ?? '').trim().split(/\s+/).filter(Boolean)
  return parts
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase())
    .join('')
})

const drawerOpen = ref(false)
const userMenu = ref<InstanceType<typeof Menu> | null>(null)

function logout() {
  auth.logout()
  router.replace({ name: 'login' })
}

const menuItems = [
  { label: 'Profil', icon: 'pi pi-user', command: () => router.push('/profile') },
  { separator: true },
  { label: 'Logout', icon: 'pi pi-sign-out', command: logout },
]

const linkBase =
  'flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors'
const linkActive = 'bg-(--p-primary-50) text-(--p-primary-color)'
const linkIdle = 'text-slate-600 hover:bg-slate-100 hover:text-slate-800'
</script>

<template>
  <header class="sticky top-0 z-30 border-b border-slate-200 bg-white">
    <div class="mx-auto flex h-16 max-w-7xl items-center gap-4 px-4 sm:px-6">
      <div class="md:hidden">
        <Button
          icon="pi pi-bars"
          severity="secondary"
          variant="text"
          aria-label="Buka menu"
          @click="drawerOpen = true"
        />
      </div>

      <!-- Logo -->
      <RouterLink to="/tickets" class="flex shrink-0 items-center gap-2">
        <img :src="apg" alt="Logo perusahaan" class="h-12 w-auto shrink-0 object-contain" />
      </RouterLink>

      <!-- Menu (desktop) -->
      <nav class="ml-4 hidden items-center gap-1 md:flex" aria-label="Navigasi utama">
        <RouterLink
          v-for="item in visibleItems"
          :key="item.to"
          v-slot="{ href, navigate, isActive }"
          :to="item.to"
          custom
        >
          <a :href="href" :class="[linkBase, isActive ? linkActive : linkIdle]" @click="navigate">
            {{ item.label }}
          </a>
        </RouterLink>
      </nav>

      <div class="ml-auto flex items-center gap-1">
        <NotificationBell />

        <!-- Menu pengguna -->
        <button
          type="button"
          class="flex items-center gap-2 rounded-lg py-1 pr-2 pl-1 hover:bg-slate-100"
          aria-haspopup="true"
          aria-controls="user_menu"
          @click="userMenu?.toggle($event)"
        >
          <Avatar
            :label="initials"
            shape="circle"
            class="bg-(--p-primary-color)! text-(--p-primary-contrast-color)!"
          />
          <span class="hidden text-left sm:block">
            <span class="block text-sm leading-tight font-medium text-slate-800">
              {{ auth.user?.name }}
            </span>
            <span class="block text-xs leading-tight text-slate-500">{{ roleLabel }}</span>
          </span>
          <i class="pi pi-chevron-down hidden text-xs text-slate-400 sm:block"></i>
        </button>
        <Menu id="user_menu" ref="userMenu" :model="menuItems" popup />
      </div>
    </div>
  </header>

  <!-- Drawer (mobile) -->
  <Drawer v-model:visible="drawerOpen" position="left" header="Menu">
    <nav class="flex flex-col gap-1" aria-label="Navigasi mobile">
      <RouterLink
        v-for="item in visibleItems"
        :key="item.to"
        v-slot="{ href, navigate, isActive }"
        :to="item.to"
        custom
      >
        <a
          :href="href"
          :class="[linkBase, isActive ? linkActive : linkIdle]"
          @click="(e) => { navigate(e); drawerOpen = false }"
        >
          <i :class="item.icon"></i>
          {{ item.label }}
        </a>
      </RouterLink>
    </nav>
  </Drawer>
</template>