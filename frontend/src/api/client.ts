import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10_000,
})

export function getErrorMessage(error: unknown, fallback = 'Terjadi kesalahan'): string {
  if (!axios.isAxiosError(error)) return fallback
  if (!error.response) return 'Tidak dapat terhubung ke server'

  const { status, data } = error.response
  if (status === 429) return 'Terlalu banyak percobaan, coba lagi sebentar lagi'
  if (status === 422) return 'Data yang dikirim tidak valid'
  if (typeof data?.detail === 'string') return data.detail

  return fallback
}