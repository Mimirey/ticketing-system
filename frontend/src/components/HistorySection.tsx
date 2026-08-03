import { useState, useEffect } from "react";
import { getTicketHistory } from "../api/ticket";
import type { TicketHistory } from "../types";

const FIELD_LABELS: Record<string, string> = {
  status: "Status",
  pic: "PIC",
  priority: "Prioritas",
};

export default function HistorySection({ ticketId }: { ticketId: number }) {
  const [history, setHistory] = useState<TicketHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTicketHistory(ticketId)
      .then(setHistory)
      .finally(() => setLoading(false));
  }, [ticketId]);
  if (loading)
    return <p className="text-sm text-slate-400">Memuat riwayat...</p>;
  if (history.length === 0)
    return (
      <p className="text-sm text-slate-400">Belum ada riwayat perubahan.</p>
    );

  return (
    <div className="space-y-3">
      {history.map((h) => (
        <div key={h.id} className="text-sm border-l-2 border-slate-200 pl-3">
          <p className="text-slate-700">
            <span className="font-medium">{h.changed_by.name}</span> mengubah{" "}
            <span className="font-medium">
              {FIELD_LABELS[h.field_changed] ?? h.field_changed}
            </span>{" "}
            dari <span className="text-slate-500">{h.old_value ?? "—"}</span> ke{" "}
            <span className="text-slate-500">{h.new_value}</span>
          </p>
          <p className="text-xs text-slate-400">
            {new Date(h.changed_at).toLocaleString("id-ID")}
          </p>
        </div>
      ))}
    </div>
  );
}
