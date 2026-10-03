import { api } from './client'

export interface Attachment {
  id: number
  original_filename: string
  file_size: number 
  content_type: string
  uploaded_by: { id: number; name: string }
  created_at: string
}

export async function uploadAttachment(ticketId: number, file: File): Promise<Attachment> {
  const body = new FormData()
  body.append('file', file) 
  const { data } = await api.post<Attachment>(`/tickets/${ticketId}/attachments`, body)
  return data
}

export async function fetchAttachments(ticketId: number): Promise<Attachment[]> {
  const { data } = await api.get<Attachment[]>(`/tickets/${ticketId}/attachments`)
  return data
}

export async function deleteAttachment(ticketId: number, attachmentId: number): Promise<void> {
  await api.delete(`/tickets/${ticketId}/attachments/${attachmentId}`)
}

async function fetchBlob(ticketId: number, attachmentId: number, kind: 'download' | 'preview') {
  const { data } = await api.get<Blob>(`/tickets/${ticketId}/attachments/${attachmentId}/${kind}`, {
    responseType: 'blob',
  })
  return data
}

export async function downloadAttachment(ticketId: number, attachment: Attachment): Promise<void> {
  const blob = await fetchBlob(ticketId, attachment.id, 'download')
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = attachment.original_filename
  a.click()
  URL.revokeObjectURL(url)
}

export async function getPreviewUrl(ticketId: number, attachmentId: number): Promise<string> {
  const blob = await fetchBlob(ticketId, attachmentId, 'preview')
  return URL.createObjectURL(blob)
}
