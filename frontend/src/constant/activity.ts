export interface ActionMeta {
  label: string
  icon: string
  badge: string // kelas Tailwind harus ditulis utuh, jangan dirakit dinamis
}

const TONE = {
  neutral: 'bg-slate-50 text-slate-600 ring-slate-500/20',
  create: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
  update: 'bg-amber-50 text-amber-700 ring-amber-600/20',
  status: 'bg-blue-50 text-blue-700 ring-blue-600/20',
  assign: 'bg-violet-50 text-violet-700 ring-violet-600/20',
  priority: 'bg-orange-50 text-orange-700 ring-orange-600/20',
  schedule: 'bg-cyan-50 text-cyan-700 ring-cyan-600/20',
  danger: 'bg-rose-50 text-rose-700 ring-rose-600/20',
} as const

const ACTIONS: Record<string, ActionMeta> = {
  LOGIN: { label: 'Login', icon: 'pi pi-sign-in', badge: TONE.neutral },

  CREATE_TICKET: { label: 'Buat ticket', icon: 'pi pi-plus-circle', badge: TONE.create },
  ASSIGN: { label: 'Assign PIC', icon: 'pi pi-user-plus', badge: TONE.assign },
  UPDATE_STATUS: { label: 'Ubah status', icon: 'pi pi-sync', badge: TONE.status },
  UPDATE_PRIORITY: { label: 'Ubah prioritas', icon: 'pi pi-flag', badge: TONE.priority },
  UPDATE_DUE_DATE: { label: 'Ubah tenggat', icon: 'pi pi-calendar', badge: TONE.schedule },
  DELETE_TICKET: { label: 'Hapus ticket', icon: 'pi pi-trash', badge: TONE.danger },

  CREATE_COMPANY: { label: 'Tambah company', icon: 'pi pi-plus-circle', badge: TONE.create },
  UPDATE_COMPANY: { label: 'Ubah company', icon: 'pi pi-pencil', badge: TONE.update },
  DELETE_COMPANY: { label: 'Hapus company', icon: 'pi pi-trash', badge: TONE.danger },

  CREATE_APPLICATION: { label: 'Tambah aplikasi', icon: 'pi pi-plus-circle', badge: TONE.create },
  UPDATE_APPLICATION: { label: 'Ubah aplikasi', icon: 'pi pi-pencil', badge: TONE.update },
  DELETE_APPLICATION: { label: 'Hapus aplikasi', icon: 'pi pi-trash', badge: TONE.danger },

  CREATE_USER: { label: 'Tambah user', icon: 'pi pi-plus-circle', badge: TONE.create },
  DELETE_USER: { label: 'Hapus user', icon: 'pi pi-trash', badge: TONE.danger },
}

export const ACTION_OPTIONS = Object.entries(ACTIONS).map(([value, meta]) => ({
  value,
  label: meta.label,
}))

export function actionMeta(action: string): ActionMeta {
  if (ACTIONS[action]) return ACTIONS[action]
  const text = action.replace(/_/g, ' ').toLowerCase()
  return {
    label: text.charAt(0).toUpperCase() + text.slice(1) || '-',
    icon: 'pi pi-circle',
    badge: TONE.neutral,
  }
}