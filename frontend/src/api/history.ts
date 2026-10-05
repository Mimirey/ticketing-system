import { api } from './client'

export interface HistoryEntry {
  id: number
  field: string
  oldValue: string | null
  newValue: string | null
  actorId: number | null
  actorName: string | null
  actorRole: string | null
  changedAt: string
}

interface HistoryResponse {
  id: number
  field_changed: string
  old_value: string | null
  new_value: string | null
  changed_by: { id: number; name: string; role?: string } | null
  changed_at: string
}

function toHistory(raw: HistoryResponse): HistoryEntry {
  return {
    id: raw.id,
    field: raw.field_changed,
    oldValue: raw.old_value,
    newValue: raw.new_value,
    actorId: raw.changed_by?.id ?? null,
    actorName: raw.changed_by?.name ?? null,
    actorRole: raw.changed_by?.role ?? null,
    changedAt: raw.changed_at,
  }
}

export async function fetchHistory(ticketId: number): Promise<HistoryEntry[]> {
  const { data } = await api.get<HistoryResponse[]>(`/tickets/${ticketId}/history`)
  return data.map(toHistory)
}
