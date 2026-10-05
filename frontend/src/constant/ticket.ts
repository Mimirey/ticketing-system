import type { SortField } from '@/api/ticket'

// Nilai persis dari app/models/enums.py
export const STATUS_OPTIONS = ['Open', 'Assigned', 'In Progress', 'QA', 'Done']
export const PRIORITY_OPTIONS = ['Low', 'Medium', 'High', 'Critical']
export const TYPE_OPTIONS = ['Bug', 'Feature Request']

export const SORT_OPTIONS: { label: string; value: SortField }[] = [
  { label: 'Tanggal Dibuat', value: 'created_at' },
  { label: 'Terakhir Diubah', value: 'updated_at' },
  { label: 'Prioritas', value: 'priority' },
  { label: 'Status', value: 'status' },
]

type Severity = 'secondary' | 'info' | 'warn' | 'success' | 'danger' | 'contrast'

export const STATUS_SEVERITY: Record<string, Severity> = {
  Open: 'secondary',
  Assigned: 'info',
  'In Progress': 'warn',
  QA: 'contrast',
  Done: 'success',
}

export const PRIORITY_SEVERITY: Record<string, Severity> = {
  Low: 'success',
  Medium: 'info',
  High: 'warn',
  Critical: 'danger',
}

export const NEXT_STATUS: Record<string, string[]> = {
  Open: ['Assigned'],
  Assigned: ['In Progress'],
  'In Progress': ['QA'],
  QA: ['Done', 'In Progress'],
  Done: [],
}
