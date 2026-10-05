import dayjs from 'dayjs'

export type DueState = 'none' | 'done' | 'overdue' | 'soon' | 'ok'

export interface DueInfo {
  state: DueState
  label: string
}

const SOON_HOURS = 24 

function humanize(totalMinutes: number): string {
  const m = Math.abs(totalMinutes)
  const days = Math.floor(m / 1440)
  const hours = Math.floor((m % 1440) / 60)
  const mins = m % 60

  if (days > 0) return hours ? `${days} hari ${hours} jam` : `${days} hari`
  if (hours > 0) return mins ? `${hours} jam ${mins} menit` : `${hours} jam`
  return `${mins} menit`
}

export function getDueInfo(dueDate: string | null, status: string): DueInfo {
  if (status === 'Done') return { state: 'done', label: 'Selesai' }
  if (!dueDate) return { state: 'none', label: 'Belum ada tenggat' }

  const diff = dayjs(dueDate).diff(dayjs(), 'minute')
  if (diff < 0) return { state: 'overdue', label: `Terlambat ${humanize(diff)}` }
  if (diff < SOON_HOURS * 60) return { state: 'soon', label: `Sisa ${humanize(diff)}` }
  return { state: 'ok', label: `Sisa ${humanize(diff)}` }
}

// Warna teks untuk label di tabel
export const DUE_TEXT_CLASS: Record<DueState, string> = {
  none: 'text-slate-400',
  done: 'text-slate-500',
  overdue: 'text-red-600',
  soon: 'text-amber-600',
  ok: 'text-slate-500',
}
