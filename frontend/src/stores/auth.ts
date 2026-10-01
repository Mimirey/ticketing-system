import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { loginRequest, type AuthUser, type LoginPayload } from '@/api/auth'

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

  async function login(payload: LoginPayload): Promise<void> {
    const result = await loginRequest(payload)
    accessToken.value = result.accessToken
    refreshToken.value = result.refreshToken
    user.value = result.user

    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        accessToken: result.accessToken,
        refreshToken: result.refreshToken,
        user: result.user,
      } satisfies StoredAuth),
    )
  }

  function logout(): void {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem(STORAGE_KEY)
  }

  return { user, accessToken, refreshToken, isAuthenticated, login, logout }
})
