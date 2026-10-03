import { api } from './client'

export interface Company {
  id: number
  name: string
}

export interface Application {
  id: number
  company_id: number
  name: string
  description: string | null
}

export async function fetchCompanies(): Promise<Company[]> {
  const { data } = await api.get<Company[]>('/companies')
  return data
}

export async function fetchApplications(companyId: number): Promise<Application[]> {
  const { data } = await api.get<Application[]>('/applications', {
    params: { company_id: companyId },
  })
  return data.filter((a) => a.company_id === companyId)
}
