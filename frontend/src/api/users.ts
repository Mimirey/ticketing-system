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

export interface UserAccount {
  id: number
  name: string
  username: string | null
  email: string
  role: string
}

interface RawUser {
  id: number
  name: string
  username?: string | null
  email: string
  role?: string | { id?: number; name: string } | null
  role_name?: string | null
}

function toAccount(raw: RawUser): UserAccount {
  const role = typeof raw.role === 'string' ? raw.role : (raw.role?.name ?? raw.role_name ?? '')

  return {
    id: raw.id,
    name: raw.name,
    username: raw.username ?? null,
    email: raw.email,
    role,
  }
}

export async function fetchAllUsers(): Promise<UserAccount[]> {
  const { data } = await api.get<RawUser[]>('/users')
  return data.map(toAccount)
}

export interface UserCreatePayload {
  username: string
  name: string
  email: string
  role_id: number
  telegram_chat_id: null
}

export async function createUser(payload: UserCreatePayload): Promise<void> {
  await api.post('/users', payload)
}

export async function deleteUser(id: number): Promise<void> {
  await api.delete(`/users/${id}`)
}

export async function changePassword(payload: {
  current_password: string
  new_password: string
}): Promise<void> {
  await api.patch('/users/me/password', payload)
}

export async function resetUserPassword(id: number): Promise<void> {
  await api.patch(`/users/${id}/reset-password`)
}