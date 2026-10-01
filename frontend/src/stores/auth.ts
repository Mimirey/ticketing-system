import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export interface User {
  id: number
  name: string
  username: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isAuthenticated = computed(() => !!token.value)

  async function login(username: string, password: string): Promise<void> {
    await new Promise((resolve) => setTimeout(resolve, 800))

    if (password !== 'password123') {
      throw new Error('Username atau password salah')
    }

    token.value = 'mock-token'
    user.value = { id: 1, name: 'Demo User', username }
  }

  function logout(): void {
    token.value = null
    user.value = null
  }

  return { user, token, isAuthenticated, login, logout }
})
