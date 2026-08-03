import type { TicketStatus } from "../types";

export const ALLOWED_TRANSITIONS: Record<TicketStatus, TicketStatus[]> ={
    Open: ["Assigned"],
    Assigned: ["In Progress"],
    "In Progress": ["QA"],
    QA: ["Done", "In Progress"],
    Done: [],
};
export function getNextStatuses(current: TicketStatus): TicketStatus[]{
    return ALLOWED_TRANSITIONS[current] ?? [];
}