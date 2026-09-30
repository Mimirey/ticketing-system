import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  getTicket,
  assignTicket,
  updateTicketStatus,
  updateTicketPriority,
} from "../api/ticket";
import { getStaffUsers } from "../api/users";
import type { Ticket, TicketPriority, User } from "../types";
import { StatusBadge, PriorityBadge } from "../components/StatusBadge";
import { getNextStatuses } from "../utils/ticketWorkflow";
import { useAuth } from "../context/AuthContext";
import CommentSection from "../components/CommentSection";
import AttachmentSection from "../components/AttachmentSection";
import HistorySection from "../components/HistorySection";
import { deleteTicket } from "../api/ticket";
import ConfirmModal from "../components/ConfirModal";

const PRIORITY_OPTIONS: TicketPriority[] = [
  "Low",
  "Medium",
  "High",
  "Critical",
];
type Tab = "comments" | "attachments" | "history";

export default function TicketDetail() {
  const { id } = useParams<{ id: string }>();
  const ticketId = Number(id);
  const navigate = useNavigate();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [staffList, setStaffList] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionError, setActionError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("comments");

  const { user } = useAuth();
  const isPM = user?.role === "PM_IT";
  const isPIC = ticket?.pic_id === user?.id; // pengecekan lebih presisi (ini PIC-nya atau bukan) di bawah

  const fetchTicket = async () => {
    setLoading(true);
    try {
      const data = await getTicket(ticketId);
      setTicket(data);
    } finally {
      setLoading(false);
    }
  };
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const confirmDeleteTicket = async () => {
    try {
      await deleteTicket(ticketId);
      navigate("/tickets");
    } catch (err: any) {
      setActionError(err.response?.data?.detail || "Gagal menghapus ticket");
    } finally {
      setShowDeleteConfirm(false);
    }
  };

  useEffect(() => {
    fetchTicket();
    if (isPM) {
      getStaffUsers().then(setStaffList);
    }
  }, [ticketId]);

  const handleAssign = async (picId: number) => {
    setActionError(null);
    try {
      const updated = await assignTicket(ticketId, picId);
      setTicket(updated);
    } catch (err: any) {
      setActionError(err.response?.data?.detail || "Gagal menugaskan ticket");
    }
  };

  const handleStatusChange = async (status: any) => {
    setActionError(null);
    try {
      const updated = await updateTicketStatus(ticketId, status);
      setTicket(updated);
    } catch (err: any) {
      setActionError(err.response?.data?.detail || "Gagal mengubah status");
    }
  };

  const handlePriorityChange = async (priority: TicketPriority) => {
    setActionError(null);
    try {
      const updated = await updateTicketPriority(ticketId, priority);
      setTicket(updated);
    } catch (err: any) {
      setActionError(err.response?.data?.detail || "Gagal mengubah prioritas");
    }
  };

  if (loading) return <div className="p-6 text-slate-400">Memuat...</div>;
  if (!ticket)
    return <div className="p-6 text-slate-400">Ticket tidak ditemukan</div>;

  const nextStatuses = getNextStatuses(ticket.status);
  const canChangeStatus = isPM || isPIC;

  const canDeleteTicket =
    ticket.status !== "Done" && (isPM || ticket.reporter_id === user?.id);

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-xs text-slate-400 mb-1">
              {ticket.ticket_number}
            </p>
            <h1 className="text-xl font-bold text-slate-800">{ticket.title}</h1>
          </div>
          <div className="flex gap-2">
            <StatusBadge status={ticket.status} />
            <PriorityBadge priority={ticket.priority} />
          </div>
        </div>

        <p className="text-sm text-slate-600 mb-4 whitespace-pre-wrap">
          {ticket.description}
        </p>

        <div className="grid grid-cols-2 gap-3 text-sm text-slate-500 mb-4">
          <span>
            Jenis: <span className="text-slate-700">{ticket.type}</span>
          </span>
          <span>
            Modul:{" "}
            <span className="text-slate-700">{ticket.module || "-"}</span>
          </span>
        </div>

        {actionError && (
          <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded">
            {actionError}
          </div>
        )}

        <div className="border-t border-slate-100 pt-4 flex flex-wrap gap-4">
          {isPM && ticket.status !== "Done" && (
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">
                Assign ke Staff IT
              </label>
              <select
                value={ticket.pic_id ?? ""}
                onChange={(e) => handleAssign(Number(e.target.value))}
                className="px-2 py-1.5 border border-slate-300 rounded-md text-sm"
              >
                <option value="" disabled>
                  Pilih Staff IT
                </option>
                {staffList.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {isPM && ticket.status !== "Done" && (
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">
                Ubah Prioritas
              </label>
              <select
                value={ticket.priority}
                onChange={(e) =>
                  handlePriorityChange(e.target.value as TicketPriority)
                }
                className="px-2 py-1.5 border border-slate-300 rounded-md text-sm"
              >
                {PRIORITY_OPTIONS.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>
          )}

          {canChangeStatus && nextStatuses.length > 0 && (
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">
                Ubah Status
              </label>
              <select
                value=""
                onChange={(e) =>
                  e.target.value && handleStatusChange(e.target.value)
                }
                className="px-2 py-1.5 border border-slate-300 rounded-md text-sm"
              >
                <option value="" disabled>
                  Pilih status berikutnya
                </option>
                {nextStatuses.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
          )}
          {canDeleteTicket && (
            <button
              onClick={()=> setShowDeleteConfirm(true)}
              className="text-sm text-red-600 hover:text-red-700 font-medium self-end"
            >
              Hapus Ticket
            </button>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        <div className="flex border-b border-slate-200">
          {(["comments", "attachments", "history"] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-3 text-sm font-medium ${
                tab === t
                  ? "text-blue-600 border-b-2 border-blue-600"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              {t === "comments"
                ? "Komentar"
                : t === "attachments"
                  ? "Lampiran"
                  : "Riwayat"}
            </button>
          ))}
        </div>

        <div className="p-4">
          {tab === "comments" && <CommentSection ticketId={ticketId} />}
          {tab === "attachments" && <AttachmentSection ticketId={ticketId} />}
          {tab === "history" && <HistorySection ticketId={ticketId} />}
        </div>
      </div>
      {showDeleteConfirm && (
        <ConfirmModal
          title="Hapus Ticket"
          message="Yakin ingin menghapus ticket ini? Aksi ini tidak dapat dibatalkan."
          onConfirm={confirmDeleteTicket}
          onCancel={() => setShowDeleteConfirm(false)}
        />
      )}
    </div>
    
  );
}
