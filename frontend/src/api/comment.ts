import dayjs from 'dayjs'
import { api } from './client'

export interface TicketComment {
  id: number
  content: string
  author: { id: number; name: string }
  created_at: string
  edited: boolean
}

interface CommentResponse {
  id: number
  content: string
  author: { id: number; name: string }
  created_at: string
  updated_at: string | null
}

function toComment(raw: CommentResponse): TicketComment {
  return {
    id: raw.id,
    content: raw.content,
    author: raw.author,
    created_at: raw.created_at,
    edited: !!raw.updated_at && dayjs(raw.updated_at).diff(raw.created_at, 'second') > 1,
  }
}

export async function fetchComments(ticketId: number): Promise<TicketComment[]> {
  const { data } = await api.get<CommentResponse[]>(`/tickets/${ticketId}/comments`)
  return data.map(toComment)
}

export async function createComment(ticketId: number, content: string): Promise<void> {
  await api.post(`/tickets/${ticketId}/comments`, { content })
}

export async function updateComment(
  ticketId: number,
  commentId: number,
  content: string,
): Promise<void> {
  await api.patch(`/tickets/${ticketId}/comments/${commentId}`, { content })
}

export async function deleteComment(ticketId: number, commentId: number): Promise<void> {
  await api.delete(`/tickets/${ticketId}/comments/${commentId}`)
}
