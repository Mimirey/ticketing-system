import { useCallback, useState, useEffect } from "react";
import type { TicketPriority, Ticket, TicketStatus } from "../types";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getTickets } from "../api/ticket";
import { StatusBadge, PriorityBadge } from "../components/StatusBadge";

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
const PAGE_SIZE = 10;

export default function TicketList() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<TicketStatus | "">("");

  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<TicketStatus | "">("");
  const [priority, setPriority] = useState<TicketPriority | "">("");
  const [page, setPage] = useState(1);

  const navigate = useNavigate();
  const { user } = useAuth();

  const fetchTickets = useCallback(async () => {
    setLoading(true);
    // setError(null);
    try {
      const data = await getTickets({
        search: search || undefined,
        status: status || undefined,
        priority: priority || undefined,
        page,
        page_size: PAGE_SIZE,
      });
      setTickets(data);
    } catch (err) {
      // setError("Gagal memuat daftar ticket");
    } finally {
      setLoading(false);
    }
  }, [search, status, priority, page]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      fetchTickets();
    }, 400);
    return () => clearTimeout(timeout);
  }, [fetchTickets]);

  const resetToFirstPage = () => setPage(1);
  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Daftar Ticket</h1>
        <button
          onClick={() => navigate("/tickets/new")}
          className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
        >
          + Buat Ticket
        </button>
      </div>

      <div className="flex gap-3 mb-4">
        <input
          type="text"
          placeholder="Cari nomor ticket, judul, atau modul..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            resetToFirstPage();
          }}
          className="flex-1 px-3 py-2 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
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
            <option key={s} value={s}>{s}</option>
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
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded">{error}</div>
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
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-slate-400">
                  Memuat...
                </td>
              </tr>
            ) : tickets.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-slate-400">
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
                  <td className="px-4 py-3 font-medium text-slate-700">{ticket.ticket_number}</td>
                  <td className="px-4 py-3 text-slate-600">{ticket.title}</td>
                  <td className="px-4 py-3 text-slate-500">{ticket.type}</td>
                  <td className="px-4 py-3"><StatusBadge status={ticket.status} /></td>
                  <td className="px-4 py-3"><PriorityBadge priority={ticket.priority} /></td>
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
    </div>
  );
}
