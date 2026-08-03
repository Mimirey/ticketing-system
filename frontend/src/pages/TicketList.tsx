import { useCallback, useState, useEffect } from "react";
import type {
  TicketPriority,
  Ticket,
  TicketStatus,
  TicketType,
  User,
} from "../types";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getTickets, deleteTicket, exportTicketsExcel, exportTicketsPdf } from "../api/ticket";
import { StatusBadge, PriorityBadge } from "../components/StatusBadge";
import { getStaffUsers } from "../api/users";
import ConfirmModal from "../components/ConfirModal";

const STATUS_OPTIONS: TicketStatus[] = [
  "Open",
  "Assigned",
  "In Progress",
  "QA",
  "Done",
];
const PRIORITY_OPTIONS: TicketPriority[] = [
  "Low",
  "Medium",
  "High",
  "Critical",
];
const TYPE_OPTIONS: TicketType[] = ["Bug", "Feature Request"];
const SORT_OPTIONS = [
  { value: "created_at", label: "Tanggal Dibuat" },
  { value: "updated_at", label: "Tanggal Diubah" },
  { value: "priority", label: "Prioritas" },
  { value: "status", label: "Status" },
];
const PAGE_SIZE = 10;

export default function TicketList() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [ticketToDelete, setTicketToDelete] = useState<Ticket | null>(null);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<TicketStatus | "">("");
  const [priority, setPriority] = useState<TicketPriority | "">("");
  const [type, setType] = useState<TicketType | "">("");
  const [picId, setPicId] = useState<string>("");
  const [sortBy, setSortBy] = useState("created_at");
  const [order, setOrder] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(1);

  const [staffList, setStaffList] = useState<User[]>([]);

  const navigate = useNavigate();
  const { user } = useAuth();
  const isPM = user?.role === "PM_IT";
  const [exporting, setExporting] = useState<"excel" | "pdf" | null>(null);

  const handleExport = async (type: "excel" | "pdf") => {
    setExporting(type);
    try {
      if (type === "excel") {
        await exportTicketsExcel();
      } else {
        await exportTicketsPdf();
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || "Gagal mengekspor data");
    } finally {
      setExporting(null);
    }
  };
  const fetchTickets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getTickets({
        search: search || undefined,
        status: status || undefined,
        priority: priority || undefined,
        type: type || undefined,
        pic_id: picId ? Number(picId) : undefined,
        sort_by: sortBy,
        order,
        page,
        page_size: PAGE_SIZE,
      });
      setTickets(data);
    } catch {
      setError("Gagal memuat daftar ticket");
    } finally {
      setLoading(false);
    }
  }, [search, status, priority, type, picId, sortBy, order, page]);

  useEffect(() => {
    const timeout = setTimeout(fetchTickets, 400);
    return () => clearTimeout(timeout);
  }, [fetchTickets]);

  useEffect(() => {
    if (isPM) getStaffUsers().then(setStaffList);
  }, [isPM]);

  const resetToFirstPage = () => setPage(1);

  const handleDeleteClick = (e: React.MouseEvent, ticket: Ticket) => {
    e.stopPropagation();
    setTicketToDelete(ticket);
  };

  const confirmDelete = async () => {
    if (!ticketToDelete) return;
    try {
      await deleteTicket(ticketToDelete.id);
      fetchTickets();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Gagal menghapus ticket");
    } finally {
      setTicketToDelete(null);
    }
  };

  const canDelete = (ticket: Ticket) => {
    if (ticket.status === "Done") return false;
    return isPM || ticket.reporter_id === user?.id;
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Daftar Ticket</h1>
        <div className="flex gap-2">
          {isPM && (
            <>
              <button
                onClick={() => handleExport("excel")}
                disabled={exporting !== null}
                className="px-3 py-2 border border-slate-300 rounded-md text-sm font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-50"
              >
                {exporting === "excel" ? "Mengekspor..." : "Export Excel"}
              </button>
              <button
                onClick={() => handleExport("pdf")}
                disabled={exporting !== null}
                className="px-3 py-2 border border-slate-300 rounded-md text-sm font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-50"
              >
                {exporting === "pdf" ? "Mengekspor..." : "Export PDF"}
              </button>
            </>
          )}
          <button
            onClick={() => navigate("/tickets/new")}
            className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
          >
            + Buat Ticket
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-3 mb-4">
        <input
          type="text"
          placeholder="Cari nomor ticket, judul, atau pelapor..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            resetToFirstPage();
          }}
          className="flex-1 min-w-[200px] px-3 py-2 border border-slate-300 rounded-md text-sm"
        />
        <select
          value={status}
          onChange={(e) => {
            setStatus(e.target.value as TicketStatus | "");
            resetToFirstPage();
          }}
          className="px-3 py-2 border border-slate-300 rounded-md text-sm"
        >
          <option value="">Semua Status</option>
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <select
          value={priority}
          onChange={(e) => {
            setPriority(e.target.value as TicketPriority | "");
            resetToFirstPage();
          }}
          className="px-3 py-2 border border-slate-300 rounded-md text-sm"
        >
          <option value="">Semua Prioritas</option>
          {PRIORITY_OPTIONS.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
        <select
          value={type}
          onChange={(e) => {
            setType(e.target.value as TicketType | "");
            resetToFirstPage();
          }}
          className="px-3 py-2 border border-slate-300 rounded-md text-sm"
        >
          <option value="">Semua Jenis</option>
          {TYPE_OPTIONS.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>

        {isPM && (
          <select
            value={picId}
            onChange={(e) => {
              setPicId(e.target.value);
              resetToFirstPage();
            }}
            className="px-3 py-2 border border-slate-300 rounded-md text-sm"
          >
            <option value="">Semua PIC</option>
            {staffList.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        )}

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-3 py-2 border border-slate-300 rounded-md text-sm"
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              Urutkan: {o.label}
            </option>
          ))}
        </select>
        <button
          onClick={() => setOrder((o) => (o === "asc" ? "desc" : "asc"))}
          className="px-3 py-2 border border-slate-300 rounded-md text-sm"
          title="Ubah arah urutan"
        >
          {order === "asc" ? "↑ Naik" : "↓ Turun"}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded">
          {error}
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-600 text-left">
            <tr>
              <th className="px-4 py-3 font-medium">Nomor</th>
              <th className="px-4 py-3 font-medium">Judul</th>
              <th className="px-4 py-3 font-medium">Tipe</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Prioritas</th>
              <th className="px-4 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td
                  colSpan={6}
                  className="px-4 py-8 text-center text-slate-400"
                >
                  Memuat...
                </td>
              </tr>
            ) : tickets.length === 0 ? (
              <tr>
                <td
                  colSpan={6}
                  className="px-4 py-8 text-center text-slate-400"
                >
                  Tidak ada ticket ditemukan
                </td>
              </tr>
            ) : (
              tickets.map((ticket) => (
                <tr
                  key={ticket.id}
                  onClick={() => navigate(`/tickets/${ticket.id}`)}
                  className="border-t border-slate-100 hover:bg-slate-50 cursor-pointer"
                >
                  <td className="px-4 py-3 font-medium text-slate-700">
                    {ticket.ticket_number}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{ticket.title}</td>
                  <td className="px-4 py-3 text-slate-500">{ticket.type}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={ticket.status} />
                  </td>
                  <td className="px-4 py-3">
                    <PriorityBadge priority={ticket.priority} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    {canDelete(ticket) && (
                      <button
                        onClick={(e) => handleDeleteClick(e, ticket)}
                        className="text-xs text-red-600 hover:text-red-700 font-medium"
                      >
                        Hapus
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between mt-4">
        <span className="text-sm text-slate-500">Halaman {page}</span>
        <div className="flex gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1.5 border border-slate-300 rounded-md text-sm disabled:opacity-40"
          >
            Sebelumnya
          </button>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={tickets.length < PAGE_SIZE}
            className="px-3 py-1.5 border border-slate-300 rounded-md text-sm disabled:opacity-40"
          >
            Selanjutnya
          </button>
        </div>
      </div>
      {ticketToDelete && (
        <ConfirmModal
          title="Hapus Ticket"
          message={`Yakin ingin menghapus ticket ${ticketToDelete.ticket_number}? Aksi ini tidak dapat dibatalkan.`}
          onConfirm={confirmDelete}
          onCancel={() => setTicketToDelete(null)}
        />
      )}
    </div>
  );
}
