import axios from 'axios'
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
  try {
    const { data } = await api.get<Blob>(
      `/tickets/${ticketId}/attachments/${attachmentId}/${kind}`,
      { responseType: 'blob' },
    )
    return data
  } catch (e) {
    // Respons error juga berupa blob. Diubah ke JSON supaya getErrorMessage bisa membaca `detail`.
    if (axios.isAxiosError(e) && e.response?.data instanceof Blob) {
      try {
        e.response.data = JSON.parse(await e.response.data.text())
      } catch {
        // bukan JSON, biarkan
      }
    }
    throw e
  }
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

// Kembalikan URL sementara untuk <img> atau <iframe>.
// Panggil URL.revokeObjectURL(url) saat dialog pratinjau ditutup.
export async function getPreviewUrl(ticketId: number, attachment: Attachment): Promise<string> {
  let blob: Blob
  try {
    blob = await fetchBlob(ticketId, attachment.id, 'preview')
  } catch (e) {
    console.warn('Endpoint preview gagal, memakai endpoint download', e)
    blob = await fetchBlob(ticketId, attachment.id, 'download')
  }
  // Paksa tipe sesuai data lampiran supaya <img> dan <iframe> menampilkannya dengan benar
  return URL.createObjectURL(new Blob([blob], { type: attachment.content_type }))
}
