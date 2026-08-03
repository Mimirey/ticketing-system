import apiClient from "./client";
import type { Ticket, TicketHistory, TicketType, TicketPriority, TicketStatus } from "../types";

export interface TicketListParams {
  search?: string;
  status?: TicketStatus;
  priority?: TicketPriority;
  type?: TicketType;
  pic_id?: number; 
  page?: number;
  page_size?: number;
  sort_by?: string;
  order?: "asc" | "desc";
}

export const getTickets = async (params: TicketListParams = {}) => {
  const res = await apiClient.get<Ticket[]>("/tickets", { params });
  return res.data;
};

export const getTicket = async (id: number) => {
  const res = await apiClient.get<Ticket>(`/tickets/${id}`);
  return res.data;
};

export const createTicket = async (data: {
  type: TicketType;
  title: string;
  description: string;
  priority: TicketPriority;
  module?: string;
}) => {
  const res = await apiClient.post<Ticket>("/tickets", data);
  return res.data;
};

export const assignTicket = async (id: number, pic_id: number) => {
  const res = await apiClient.patch<Ticket>(`/tickets/${id}/assign`, { pic_id });
  return res.data;
};

export const updateTicketStatus = async (id: number, status: TicketStatus) => {
  const res = await apiClient.patch<Ticket>(`/tickets/${id}/status`, { status });
  return res.data;
};

export const updateTicketPriority = async (id: number, priority: TicketPriority) => {
  const res = await apiClient.patch<Ticket>(`/tickets/${id}/priority`, { priority });
  return res.data;
};

export const getTicketHistory = async (id: number) => {
  const res = await apiClient.get<TicketHistory[]>(`/tickets/${id}/history`);
  return res.data;
};

export const deleteTicket = async (id: number) => {
  const res = await apiClient.delete(`/tickets/${id}`);
  return res.data;
};