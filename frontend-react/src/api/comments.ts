import apiClient from "./client";
import type {Comment} from "../types";

export const getComments = async (ticketId: number) => {
  const res = await apiClient.get<Comment[]>(`/tickets/${ticketId}/comments`);
  return res.data;
};
export const createComment = async (ticketId: number, content: string) => {
  const res = await apiClient.post<Comment>(`/tickets/${ticketId}/comments`, { content });
  return res.data;
};
export const updateComment = async (ticketId: number, commentId: number, content: string) => {
  const res = await apiClient.patch<Comment>(`/tickets/${ticketId}/comments/${commentId}`, { content });
  return res.data;
};
export const deleteComment = async (ticketId: number, commentId: number) => {
  await apiClient.delete(`/tickets/${ticketId}/comments/${commentId}`);
};