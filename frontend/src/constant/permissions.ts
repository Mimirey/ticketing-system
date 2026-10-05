export type Role = 'USER' | 'ADMIN' | 'PM_IT' | 'STAFF_IT'

export type Permission =
  | 'ticket:create'
  | 'ticket:assign'
  | 'ticket:handle'
  | 'ticket:export'
  | 'user:manage'
  | 'master:manage'
  | 'report:view'
  | 'activity-log:view'

export const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  USER: ['ticket:create'],
  ADMIN: ['ticket:create', 'report:view'],
  PM_IT: [
    'ticket:create',
    'ticket:assign',
    'ticket:handle',
    'ticket:export',
    'user:manage',
    'master:manage',
    'report:view',
    'activity-log:view',
  ],
  STAFF_IT: ['ticket:handle'],
}

export const ROLE_LABELS: Record<Role, string> = {
  USER: 'User',
  ADMIN: 'Admin',
  PM_IT: 'PM IT',
  STAFF_IT: 'Staff IT',
}
