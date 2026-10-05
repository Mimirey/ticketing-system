import { api } from './client'

export interface AppNotification {
  id: number
  title: string
  message: string
  ticketId: number | null
  isRead: boolean
  createdAt: string
}

// SESUAIKAN: pemetaan dari respons backend. Menerima beberapa nama field umum.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function toNotification(raw: any): AppNotification {
  return {
    id: raw.id,
    title: raw.title ?? '',
    message: raw.message ?? '',
    ticketId: raw.ticket_id ?? raw.ticket?.id ?? null,
    isRead: !!(raw.is_read ?? raw.read ?? false),
    createdAt: raw.created_at,
  }
}

export async function fetchNotifications(): Promise<AppNotification[]> {
  const { data } = await api.get('/notifications')
  const list = Array.isArray(data) ? data : (data.items ?? [])
  return list.map(toNotification)
}

export async function fetchUnreadCount(): Promise<number> {
  const { data } = await api.get('/notifications/unread-count')
  if (typeof data === 'number') return data
  return data.unread_count ?? data.count ?? data.unread ?? 0 // SESUAIKAN
}

export async function markNotificationRead(id: number): Promise<void> {
  await api.patch(`/notifications/${id}/read`)
}
