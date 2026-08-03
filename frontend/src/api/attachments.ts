// src/api/attachments.ts
import apiClient from "./client";
import type { Attachment } from "../types";

export const getAttachments = async (ticketId: number) => {
  const res = await apiClient.get<Attachment[]>(`/tickets/${ticketId}/attachments`);
  return res.data;
};
export const uploadAttachment = async (ticketId: number, file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await apiClient.post<Attachment>(
    `/tickets/${ticketId}/attachments`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return res.data;
};
export const deleteAttachment = async (ticketId: number, attachmentId: number) => {
  await apiClient.delete(`/tickets/${ticketId}/attachments/${attachmentId}`);
};
export const downloadAttachment = async (ticketId: number, attachmentId: number, filename: string) => {
  const res = await apiClient.get(`/tickets/${ticketId}/attachments/${attachmentId}/download`, {
    responseType: "blob",
  });
  const url = window.URL.createObjectURL(new Blob([res.data]));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  window.URL.revokeObjectURL(url);
};