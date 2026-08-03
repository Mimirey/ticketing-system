import { useState, useEffect } from "react";
import { getActivityLogs } from "../api/activityLog";
import type { ActivityLog } from "../types";

const ACTION_LABELS: Record<string, string> = {
  LOGIN: "Login",
  CREATE_TICKET: "Buat Ticket",
  ASSIGN: "Assign Ticket",
  UPDATE_STATUS: "Ubah Status",
  DELETE_TICKET: "Hapus Ticket",
};

const ACTION_COLORS: Record<string, string> = {
  LOGIN: "bg-slate-100 text-slate-600",
  CREATE_TICKET: "bg-blue-100 text-blue-600",
  ASSIGN: "bg-purple-100 text-purple-600",
  UPDATE_STATUS: "bg-amber-100 text-amber-600",
  DELETE_TICKET: "bg-red-100 text-red-600",
};

const PAGE_SIZE = 20;

export default function ActivityLogPage() {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getActivityLogs(page, PAGE_SIZE)
      .then(setLogs)
      .finally(() => setLoading(false));
  }, [page]);

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-xl font-bold text-slate-800 mb-6">Activity Log</h1>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
        {loading ? (
          <p className="px-4 py-8 text-center text-sm text-slate-400">Memuat...</p>
        ) : logs.length === 0 ? (
          <p className="px-4 py-8 text-center text-sm text-slate-400">Belum ada aktivitas</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600 text-left">
              <tr>
                <th className="px-4 py-3 font-medium">Aksi</th>
                <th className="px-4 py-3 font-medium">Deskripsi</th>
                <th className="px-4 py-3 font-medium">Waktu</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} className="border-t border-slate-100">
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${ACTION_COLORS[log.action] ?? "bg-slate-100 text-slate-600"}`}>
                      {ACTION_LABELS[log.action] ?? log.action}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{log.description}</td>
                  <td className="px-4 py-3 text-slate-400 text-xs">
                    {new Date(log.created_at).toLocaleString("id-ID")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
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
            disabled={logs.length < PAGE_SIZE}
            className="px-3 py-1.5 border border-slate-300 rounded-md text-sm disabled:opacity-40"
          >
            Selanjutnya
          </button>
        </div>
      </div>
    </div>
  );
}