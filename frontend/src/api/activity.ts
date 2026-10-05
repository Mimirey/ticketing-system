import { api } from './client'

export interface ActivityLog {
  id: number
  action: string
  description: string
  userId: number | null
  userName: string | null
  createdAt: string
}

export interface ActivityParams {
  page?: number
  page_size?: number
  action?: string
}

interface RawLog {
  id: number
  action?: string
  action_type?: string
  description?: string
  detail?: string
  message?: string
  user?: { id: number; name: string } | null
  user_id?: number | null
  user_name?: string | null
  created_at?: string
  timestamp?: string
}

function toLog(raw: RawLog): ActivityLog {
  return {
    id: raw.id,
    action: raw.action ?? raw.action_type ?? '',
    description: raw.description ?? raw.detail ?? raw.message ?? '',
    userId: raw.user?.id ?? raw.user_id ?? null,
    userName: raw.user?.name ?? raw.user_name ?? null,
    createdAt: raw.created_at ?? raw.timestamp ?? '',
  }
}

export async function fetchActivityLogs(params: ActivityParams): Promise<ActivityLog[]> {
  const { data } = await api.get('/activity-logs', { params })
  const list: RawLog[] = Array.isArray(data) ? data : (data.items ?? [])
  return list.map(toLog)
}
