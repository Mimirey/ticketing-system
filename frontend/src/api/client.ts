import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10_000,
})

api.interceptors.request.use(async (config) => {
  const { useAuthStore } = await import('@/stores/auth')
  const token = useAuthStore().accessToken
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const isAuthEndpoint = error.config?.url?.startsWith('/auth/')

    if (axios.isAxiosError(error) && error.response?.status === 401 && !isAuthEndpoint) {
      const { useAuthStore } = await import('@/stores/auth')
      const { default: router } = await import('@/router')

      useAuthStore().logout()
      if (router.currentRoute.value.name !== 'login') {
        router.push({
          name: 'login',
          query: { redirect: router.currentRoute.value.fullPath },
        })
      }
    }
    return Promise.reject(error)
  },
)

export function getErrorMessage(error: unknown, fallback = 'Terjadi kesalahan'): string {
  if (!axios.isAxiosError(error)) return fallback
  if (!error.response) return 'Tidak dapat terhubung ke server'

  const { status, data } = error.response
  if (status === 429) return 'Terlalu banyak percobaan, coba lagi sebentar lagi'

  if (typeof data?.detail === 'string') return data.detail

  if (status === 422 && Array.isArray(data?.detail)) {
    const first = data.detail[0]
    const field = Array.isArray(first?.loc) ? first.loc[first.loc.length - 1] : null
    return field ? `${field}: ${first.msg}` : (first?.msg ?? 'Data yang dikirim tidak valid')
  }

  if (status === 422) return 'Data yang dikirim tidak valid'
  return fallback
}
