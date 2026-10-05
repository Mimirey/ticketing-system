import { api } from './client'

export interface Ticket {
  id: number
  ticket_number: string
  type: string
  title: string
  description: string
  priority: string
  status: string
  module: string
  due_date: string | null
  company_id: number
  application_id: number
  sla_status: string
  remaining_hours: number
  reporter_id: number
  pic_id: number | null
  created_at: string
  updated_at: string
}

export type SortField = 'created_at' | 'updated_at' | 'priority' | 'status'

export interface TicketListParams {
  search?: string
  status?: string
  priority?: string
  type?: string
  pic_id?: number
  page?: number
  page_size?: number
  sort_by?: SortField
  order?: 'asc' | 'desc'
}

export async function fetchTickets(params: TicketListParams): Promise<Ticket[]> {
  const { data } = await api.get<Ticket[]>('/tickets', { params })
  return data
}

export async function downloadExport(kind: 'excel' | 'pdf'): Promise<void> {
  const path = kind === 'excel' ? '/tickets/export' : '/tickets/export/pdf'
  const { data } = await api.get<Blob>(path, { responseType: 'blob' })

  const url = URL.createObjectURL(data)
  const a = document.createElement('a')
  a.href = url
  a.download = kind === 'excel' ? 'tickets.xlsx' : 'tickets.pdf'
  a.click()
  URL.revokeObjectURL(url)
}

export interface TicketCreatePayload {
  type: string
  title: string
  description: string
  priority: string
  module?: string
  company_id: number
  application_id: number
}

export async function createTicket(payload: TicketCreatePayload): Promise<Ticket> {
  const { data } = await api.post<Ticket>('/tickets', payload)
  return data
}

export async function fetchTicket(id: number): Promise<Ticket> {
  const { data } = await api.get<Ticket>(`/tickets/${id}`)
  return data
}

export async function assignTicket(id: number, picId: number): Promise<Ticket> {
  const { data } = await api.patch<Ticket>(`/tickets/${id}/assign`, { pic_id: picId })
  return data
}

export async function updateTicketStatus(id: number, status: string): Promise<Ticket> {
  const { data } = await api.patch<Ticket>(`/tickets/${id}/status`, { status })
  return data
}

export async function updateTicketPriority(id: number, priority: string): Promise<Ticket> {
  const { data } = await api.patch<Ticket>(`/tickets/${id}/priority`, { priority })
  return data
}

export async function deleteTicket(id: number): Promise<void> {
  await api.delete(`/tickets/${id}`)
}

export async function updateTicketDueDate(id: number, dueDate: string): Promise<Ticket> {
  const { data } = await api.patch<Ticket>(`/tickets/${id}/due-date`, { due_date: dueDate })
  return data
}

