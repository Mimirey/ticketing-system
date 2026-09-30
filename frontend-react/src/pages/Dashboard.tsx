import { useState, useEffect } from "react";
import {
  BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { getDashboardStatistics, getStatusChart, getPriorityChart } from "../api/dashboard";
import type { DashboardStatistics, StatusChartItem, PriorityChartItem } from "../types";

const STATUS_COLORS: Record<string, string> = {
  Open: "#94a3b8",
  Assigned: "#3b82f6",
  "In Progress": "#f59e0b",
  QA: "#a855f7",
  Done: "#22c55e",
};

const PRIORITY_COLORS: Record<string, string> = {
  Low: "#94a3b8",
  Medium: "#3b82f6",
  High: "#f97316",
  Critical: "#ef4444",
};

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
      <p className="text-xs text-slate-500 mb-1">{label}</p>
      <p className="text-2xl font-bold text-slate-800">{value}</p>
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStatistics | null>(null);
  const [statusData, setStatusData] = useState<StatusChartItem[]>([]);
  const [priorityData, setPriorityData] = useState<PriorityChartItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getDashboardStatistics(), getStatusChart(), getPriorityChart()])
      .then(([s, statusChart, priorityChart]) => {
        setStats(s);
        setStatusData(statusChart);
        setPriorityData(priorityChart);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6 text-slate-400">Memuat dashboard...</div>;
  if (!stats) return <div className="p-6 text-slate-400">Gagal memuat data dashboard</div>;

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-xl font-bold text-slate-800 mb-6">Dashboard</h1>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        <StatCard label="Total Ticket" value={stats.total_ticket} />
        <StatCard label="Open" value={stats.open_ticket} />
        <StatCard label="Assigned" value={stats.assigned_ticket} />
        <StatCard label="In Progress" value={stats.in_progress_ticket} />
        <StatCard label="QA" value={stats.qa_ticket} />
        <StatCard label="Done" value={stats.done_ticket} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
          <h2 className="text-sm font-medium text-slate-700 mb-4">Ticket berdasarkan Status</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={statusData}>
              <XAxis dataKey="status" tick={{ fontSize: 12 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {statusData.map((entry, index) => (
                  <Cell key={index} fill={STATUS_COLORS[entry.status] ?? "#94a3b8"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
          <h2 className="text-sm font-medium text-slate-700 mb-4">Ticket berdasarkan Prioritas</h2>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={priorityData}
                dataKey="count"
                nameKey="priority"
                cx="50%"
                cy="50%"
                outerRadius={90}
                label={(entry: any) => `${entry.priority}: ${entry.count}`}
              >
                {priorityData.map((entry, index) => (
                  <Cell key={index} fill={PRIORITY_COLORS[entry.priority] ?? "#94a3b8"} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}