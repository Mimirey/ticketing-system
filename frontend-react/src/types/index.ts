export type TicketType = "Bug" | "Feature Request";
export type TicketPriority = "Low" | "Medium" | "High" | "Critical";
export type TicketStatus = "Open" | "Assigned" | "In Progress" | "QA" | "Done";

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}
export interface Ticket {
  id: number;
  ticket_number: string;
  type: TicketType;
  title: string;
  description: string;
  priority: TicketPriority;
  status: TicketStatus;
  module: string | null;
  reporter_id: number;
  pic_id: number | null;
  created_at: string;
  updated_at: string;
}
export interface TicketHistory {
  id: number;
  field_changed: string;
  old_value: string | null;
  new_value: string;
  changed_by: { id: number; name: string };
  changed_at: string;
}
export interface Comment {
  id: number;
  content: string;
  author: { id: number; name: string };
  created_at: string;
  updated_at: string;
}
export interface Attachment {
  id: number;
  original_filename: string;
  file_size: number;
  content_type: string;
  uploaded_by: { id: number; name: string };
  created_at: string;
}
export interface Notification {
  id: number;
  title: string;
  message: string;
  is_read: boolean;
  ticket_id: number | null;
  created_at: string;
}
export interface LoginResponse {
  access_token: string;
  token_type: string;
  id: number;
  role: string;
  name: string;
}
export interface DashboardStatistics {
  total_ticket: number;
  open_ticket: number;
  assigned_ticket: number;
  in_progress_ticket: number;
  qa_ticket: number;
  done_ticket: number;
  high_priority_ticket: number;
  medium_priority_ticket: number;
  low_priority_ticket: number;
  critical_priority_ticket: number;
}

export interface StatusChartItem {
  status: string;
  count: number;
}
export interface PriorityChartItem {
  priority: string;
  count: number;
}
export interface ActivityLog{
  id: number;
  action: string;
  description: string;
  user : {id:number; name:string} | null;
  created_at: string;
}