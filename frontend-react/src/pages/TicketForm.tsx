import {useState, type FormEvent } from "react";
import type { TicketPriority, TicketType } from "../types";
import { useNavigate } from "react-router-dom";
import { createTicket } from "../api/ticket";

const TYPE_OPTIONS: TicketType[] = ["Bug", "Feature Request"];
const PRIORITY_OPTIONS: TicketPriority[] = [
  "Low",
  "Medium",
  "High",
  "Critical",
];
export default function TicketForm() {
  const [type, setType] = useState<TicketType>("Bug");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TicketPriority>("Low");
  const [module, setModule] = useState("");

  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      const ticket = await createTicket({
        type,
        title,
        description,
        priority,
        module: module || undefined,
      });
      navigate(`/tickets/${ticket.id}`);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((d: any) => d.msg).join(", "));
      } else {
        setError(detail || "Gagal membuat ticket");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-xl font-bold text-slate-800 mb-6">
        Buat Ticket Baru
      </h1>

      <form
        onSubmit={handleSubmit}
        className="bg-white p-6 rounded-lg shadow-sm border border-slate-200"
      >
        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded">
            {error}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Jenis Ticket
            </label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value as TicketType)}
              className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
            >
              {TYPE_OPTIONS.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Prioritas
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as TicketPriority)}
              className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
            >
              {PRIORITY_OPTIONS.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Judul
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            minLength={5}
            maxLength={200}
            placeholder="Ringkasan singkat masalah/permintaan"
            className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Modul Aplikasi
          </label>
          <input
            type="text"
            value={module}
            onChange={(e) => setModule(e.target.value)}
            placeholder="Contoh: Login, Dashboard, Pembayaran (opsional)"
            className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Deskripsi
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            minLength={10}
            rows={5}
            placeholder="Jelaskan detail masalah atau permintaan fitur..."
            className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={submitting}
            className="bg-blue-600 text-white px-5 py-2 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {submitting ? "Menyimpan..." : "Buat Ticket"}
          </button>
          <button
            type="button"
            onClick={() => navigate("/tickets")}
            className="px-5 py-2 rounded-md text-sm font-medium text-slate-600 hover:bg-slate-100"
          >
            Batal
          </button>
        </div>
      </form>
    </div>
  );
}
