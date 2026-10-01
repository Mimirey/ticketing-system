import { api } from './client'

export interface AuthUser {
  id: number
  name: string
  role: string
}

export interface LoginPayload {
  identifier: string
  password: string
  captchaId: string
  captchaAnswer: number
}

export interface LoginResult {
  accessToken: string
  refreshToken: string
  user: AuthUser
}

export async function loginRequest(payload: LoginPayload): Promise<LoginResult> {
  const { data } = await api.post('/auth/login', {
    identifier: payload.identifier,
    password: payload.password,
    captcha_id: payload.captchaId,
    captcha_answer: payload.captchaAnswer,
  })

  return {
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
    user: { id: data.id, name: data.name, role: data.role },
  }
}
