import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { loginRequest, type AuthUser, type LoginPayload } from '@/api/auth'
import { ROLE_PERMISSIONS, type Permission, type Role } from '@/constant/permissions'

const STORAGE_KEY = 'auth'

interface StoredAuth {
  accessToken: string
  refreshToken: string
  user: AuthUser
}

function loadStored(): StoredAuth | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as StoredAuth) : null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const stored = loadStored()

  const accessToken = ref<string | null>(stored?.accessToken ?? null)
  const refreshToken = ref<string | null>(stored?.refreshToken ?? null)
  const user = ref<AuthUser | null>(stored?.user ?? null)
  const isAuthenticated = computed(() => !!accessToken.value)

  function persist() {
    if (!accessToken.value || !refreshToken.value || !user.value) return
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        accessToken: accessToken.value,
        refreshToken: refreshToken.value,
        user: user.value,
      } satisfies StoredAuth),
    )
  }

  async function login(payload: LoginPayload): Promise<void> {
    const result = await loginRequest(payload)
    accessToken.value = result.accessToken
    refreshToken.value = result.refreshToken
    user.value = result.user
    persist()
  }

  // Dipakai interceptor setelah token diperpanjang
  function setTokens(access: string, refresh: string): void {
    accessToken.value = access
    refreshToken.value = refresh
    persist()
  }

  function logout(): void {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem(STORAGE_KEY)
  }

  function can(permission: Permission): boolean {
    const role = user.value?.role as Role | undefined
    return !!role && (ROLE_PERMISSIONS[role]?.includes(permission) ?? false)
  }

  return { user, accessToken, refreshToken, isAuthenticated, login, setTokens, logout, can }
})
