type Severity = 'secondary' | 'info' | 'warn' | 'success' | 'danger' | 'contrast'

interface ActionMeta {
  label: string
  severity: Severity
}

const ACTIONS: Record<string, ActionMeta> = {
  LOGIN: { label: 'Login', severity: 'secondary' },
  CREATE_TICKET: { label: 'Buat ticket', severity: 'info' },
  ASSIGN: { label: 'Assign PIC', severity: 'contrast' },
  UPDATE_STATUS: { label: 'Ubah status', severity: 'warn' },
  DELETE_TICKET: { label: 'Hapus ticket', severity: 'danger' },
}

export const ACTION_OPTIONS = Object.entries(ACTIONS).map(([value, meta]) => ({
  value,
  label: meta.label,
}))

export function actionMeta(action: string): ActionMeta {
  if (ACTIONS[action]) return ACTIONS[action]
  const text = action.replace(/_/g, ' ').toLowerCase()
  return { label: text.charAt(0).toUpperCase() + text.slice(1) || '-', severity: 'secondary' }
}
