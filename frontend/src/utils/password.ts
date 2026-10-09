export const PASSWORD_MIN_LENGTH = 6
export const PASSWORD_MIN_UNIQUE = 4

export interface PasswordRule {
  label: string
  message: string
  test: (value: string) => boolean
}

export const PASSWORD_RULES: PasswordRule[] = [
  {
    label: `Minimal ${PASSWORD_MIN_LENGTH} karakter`,
    message: `Password minimal ${PASSWORD_MIN_LENGTH} karakter`,
    test: (value) => [...value].length >= PASSWORD_MIN_LENGTH,
  },
  {
    label: 'Minimal 1 huruf kapital',
    message: 'Password harus memiliki minimal 1 huruf kapital',
    test: (value) => /[A-Z]/.test(value),
  },
  {
    label: `Minimal ${PASSWORD_MIN_UNIQUE} karakter unik`,
    message: `Password harus memiliki minimal ${PASSWORD_MIN_UNIQUE} karakter unik`,
    test: (value) => new Set(value).size >= PASSWORD_MIN_UNIQUE,
  },
]

export function validatePassword(value: string): string {
  if (!value) return 'Password wajib diisi'
  return PASSWORD_RULES.find((rule) => !rule.test(value))?.message ?? ''
}
