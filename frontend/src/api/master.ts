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

export interface CompanyPayload {
  name: string
}

export async function createCompany(payload: CompanyPayload): Promise<Company> {
  const { data } = await api.post<Company>('/companies', payload)
  return data
}

export async function updateCompany(id: number, payload: CompanyPayload): Promise<Company> {
  const { data } = await api.put<Company>(`/companies/${id}`, payload)
  return data
}

export async function deleteCompany(id: number): Promise<void> {
  await api.delete(`/companies/${id}`)
}

export interface ApplicationPayload {
  company_id: number
  name: string
  description: string
}

export async function fetchAllApplications(): Promise<Application[]> {
  const { data } = await api.get<Application[]>('/applications')
  return data
}

export async function createApplication(payload: ApplicationPayload): Promise<Application> {
  const { data } = await api.post<Application>('/applications', payload)
  return data
}

export async function updateApplication(
  id: number,
  payload: ApplicationPayload,
): Promise<Application> {
  const { data } = await api.put<Application>(`/applications/${id}`, payload)
  return data
}

export async function deleteApplication(id: number): Promise<void> {
  await api.delete(`/applications/${id}`)
}
