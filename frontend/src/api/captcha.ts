import { api } from './client'

export interface CaptchaChallenge {
  captchaId: string
  question: string
}

export const CAPTCHA_EXPIRE_MS = 300_000

export async function fetchCaptcha(): Promise<CaptchaChallenge> {
  const { data } = await api.get('/auth/captcha')
  return { captchaId: data.captcha_id, question: data.question }
}
