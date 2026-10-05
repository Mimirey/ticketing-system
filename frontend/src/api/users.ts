import { api } from './client'

export interface UserSummary {
  id: number
  name: string
}

export async function fetchUsers(role?: string): Promise<UserSummary[]> {
  const { data } = await api.get<UserSummary[]>('/users', {
    params: role ? { role } : undefined,
  })
  return data
}

export interface MyProfile {
  id: number
  name: string
  username?: string | null
  email: string
  role: string
  telegram_linked?: boolean 
}

export async function fetchMe(): Promise<MyProfile> {
  const { data } = await api.get<MyProfile>('/users/me')
  return data
}

export interface TelegramLink {
  telegram_link: string
  expires_at: string
}

export async function createTelegramLink(): Promise<TelegramLink> {
  const { data } = await api.post<TelegramLink>('/users/me/telegram/link')
  return data
}