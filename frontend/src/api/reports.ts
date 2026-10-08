import { api } from '@/api/client'

export type TicketStatus = 'OPEN' | 'ASSIGNED' | 'IN_PROGRESS' | 'QA' | 'DONE'

export type StatusCounts = Record<TicketStatus, number>

export interface StaffReport {
  staff_id: number
  staff_name: string
  total: number
  by_status: StatusCounts
}

export interface TicketReport {
  period: Record<string, unknown>
  total: number
  by_status: StatusCounts
  by_staff: StaffReport[]
}

export interface ReportParams {
  start_date: string
  end_date: string
}

export async function fetchTicketReport(params: ReportParams): Promise<TicketReport> {
  const { data } = await api.get<TicketReport>('/reports/tickets', { params })
  return data
}
