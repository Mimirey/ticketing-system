import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10_000,
})

type RetryConfig = InternalAxiosRequestConfig & { _retry?: boolean }

api.interceptors.request.use(async (config) => {
  const { useAuthStore } = await import('@/stores/auth')
  const token = useAuthStore().accessToken
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let refreshing: Promise<string> | null = null

async function refreshAccessToken(): Promise<string> {
  const { useAuthStore } = await import('@/stores/auth')
  const auth = useAuthStore()
  if (!auth.refreshToken) throw new Error('Tidak ada refresh token')

  const { data } = await axios.post(
    `${import.meta.env.VITE_API_BASE_URL}/auth/refresh`,
    { refresh_token: auth.refreshToken },
    { timeout: 10_000 },
  )

  auth.setTokens(data.access_token, data.refresh_token ?? auth.refreshToken)
  return data.access_token as string
}

async function expireSession() {
  const { useAuthStore } = await import('@/stores/auth')
  const { default: router } = await import('@/router')
  const auth = useAuthStore()
  const hadSession = auth.isAuthenticated

  auth.logout()

  if (router.currentRoute.value.name !== 'login') {
    router.push({
      name: 'login',
      query: {
        redirect: router.currentRoute.value.fullPath,
        ...(hadSession ? { expired: '1' } : {}),
      },
    })
  }
}

api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const config = error.config as RetryConfig | undefined
    const isAuthEndpoint = config?.url?.startsWith('/auth/')

    if (error.response?.status !== 401 || !config || isAuthEndpoint) {
      return Promise.reject(error)
    }

    if (config._retry) {
      await expireSession()
      return Promise.reject(error)
    }

    config._retry = true

    try {
      if (!refreshing) {
        refreshing = refreshAccessToken().finally(() => {
          refreshing = null
        })
      }

      const token = await refreshing
      config.headers.Authorization = `Bearer ${token}`

      return api(config)
    } catch {
      await expireSession()
      return Promise.reject(error)
    }
  },
)

const FIELD_LABELS: Record<string, string> = {
  title: 'Judul',
  description: 'Deskripsi',
  module: 'Modul',
  type: 'Jenis ticket',
  priority: 'Prioritas',
  status: 'Status',
  company_id: 'Company',
  application_id: 'Aplikasi',
  pic_id: 'PIC',
  content: 'Komentar',
  file: 'File',
  identifier: 'Username',
  password: 'Password',
  captcha_answer: 'Jawaban captcha',
  name: 'Nama',
}

interface ValidationIssue {
  loc?: (string | number)[]
  msg?: string
  type?: string
  ctx?: Record<string, unknown>
}

function issueKey(issue: ValidationIssue): string {
  return String(issue.loc?.[issue.loc.length - 1] ?? '')
}

function translateIssue(issue: ValidationIssue): string {
  const key = issueKey(issue)
  const field = FIELD_LABELS[key] ?? key
  const ctx = issue.ctx ?? {}

  switch (issue.type) {
    case 'missing':
      return `${field} wajib diisi`
    case 'string_too_short':
      return `${field} minimal ${ctx.min_length} karakter`
    case 'string_too_long':
      return `${field} maksimal ${ctx.max_length} karakter`
    case 'string_type':
    case 'int_parsing':
    case 'int_type':
    case 'enum':
    case 'literal_error':
      return `${field} tidak valid`
    case 'greater_than_equal':
      return `${field} minimal ${ctx.ge}`
    case 'less_than_equal':
      return `${field} maksimal ${ctx.le}`
    default:
      return field ? `${field}: ${issue.msg ?? 'tidak valid'}` : (issue.msg ?? 'Data tidak valid')
  }
}

function issuesOf(error: unknown): ValidationIssue[] {
  if (!axios.isAxiosError(error)) return []
  const detail = error.response?.data?.detail
  return error.response?.status === 422 && Array.isArray(detail) ? detail : []
}

export function getFieldErrors(error: unknown): Record<string, string> {
  const result: Record<string, string> = {}

  for (const issue of issuesOf(error)) {
    const key = issueKey(issue)
    if (key && !result[key]) result[key] = translateIssue(issue)
  }

  return result
}

export function getErrorMessage(error: unknown, fallback = 'Terjadi kesalahan'): string {
  if (!axios.isAxiosError(error)) return fallback
  if (!error.response) return 'Tidak dapat terhubung ke server'

  const { status, data } = error.response

  if (status === 429) {
    return 'Terlalu banyak percobaan, coba lagi sebentar lagi'
  }

  if (typeof data?.detail === 'string') return data.detail

  const issues = issuesOf(error)

  if (issues.length) {
    return [...new Set(issues.map(translateIssue))].join('. ')
  }

  if (status === 422) return 'Data yang dikirim tidak valid'

  return fallback
}

export function getErrorStatus(error: unknown): number | null {
  return axios.isAxiosError(error) ? (error.response?.status ?? 0) : null
}
