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

export class EmptyFileError extends Error {}

export async function downloadExport(kind: 'excel' | 'pdf'): Promise<void> {
  const path = kind === 'excel' ? '/tickets/export' : '/tickets/export/pdf'
  const response = await api.get<Blob>(path, { responseType: 'blob' })
  const data = response.data

  if (!data || data.size === 0) {
    throw new EmptyFileError(
      'Unduhan tidak diterima browser. Jika Anda menggunakan download manager (seperti IDM), nonaktifkan untuk situs ini lalu coba lagi.',
    )
  }

  // Coba ambil nama file dari header Content-Disposition
  const contentDisposition = response.headers['content-disposition']
  let filename = ''

  if (contentDisposition) {
    const match = contentDisposition.match(/filename="?([^"]+)"?/)
    if (match && match[1]) {
      filename = match[1]
    }
  }

  // Fallback jika header tidak ada: buat nama file dinamis dengan timestamp
  if (!filename) {
    const now = new Date()
    const timestamp =
      now.getFullYear().toString() +
      String(now.getMonth() + 1).padStart(2, '0') +
      String(now.getDate()).padStart(2, '0') +
      '_' +
      String(now.getHours()).padStart(2, '0') +
      String(now.getMinutes()).padStart(2, '0') +
      String(now.getSeconds()).padStart(2, '0')

    const ext = kind === 'excel' ? 'xlsx' : 'pdf'
    filename = `Laporan_Ticket_${timestamp}.${ext}`
  }

  const url = URL.createObjectURL(data)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 10_000)
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
