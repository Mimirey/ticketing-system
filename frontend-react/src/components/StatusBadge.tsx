import type { TicketStatus, TicketPriority } from "../types";

const STATUS_STYLES: Record<TicketStatus, string> = {
  Open: "bg-slate-100 text-slate-700",
  Assigned: "bg-blue-100 text-blue-700",
  "In Progress": "bg-amber-100 text-amber-700",
  QA: "bg-purple-100 text-purple-700",
  Done: "bg-green-100 text-green-700",
};

const PRIORITY_STYLES: Record<TicketPriority, string> = {
  Low: "bg-slate-100 text-slate-600",
  Medium: "bg-blue-100 text-blue-600",
  High: "bg-orange-100 text-orange-600",
  Critical: "bg-red-100 text-red-700",
};

export function StatusBadge({status}: {status: TicketStatus}) {
    return(
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_STYLES[status]}`}>
            {status}
        </span>
    )
}
export function PriorityBadge({priority}: {priority: TicketPriority}){
    return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${PRIORITY_STYLES[priority]}`}>
            {priority}
        </span>
    )
}