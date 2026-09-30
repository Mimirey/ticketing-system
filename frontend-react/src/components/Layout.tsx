import { type ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import NotificationBell from "./NotificationBell";

export default function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <span className="font-bold text-slate-800">Ticketing System</span>
          <Link to="/tickets" className="text-sm text-slate-600 hover:text-blue-600">Tickets</Link>
          <Link to="/dashboard" className="text-sm text-slate-600 hover:text-blue-600">Dashboard</Link>
          {user?.role === "PM_IT" && (
            <Link to="/activity-logs" className="text-sm text-slate-600 hover:text-blue-600">
              Activity Log
            </Link>
          )}
          <Link to="/profile" className="text-sm text-slate-600 hover:text-blue-600">
            Profile
          </Link>
        </div>
        
        <div className="flex items-center gap-4">
          <NotificationBell />
          <span className="text-sm text-slate-600">
            {user?.name} <span className="text-slate-400">({user?.role})</span>
          </span>
          <button onClick={handleLogout} className="text-sm text-red-600 hover:text-red-700 font-medium">
            Logout
          </button>
        </div>
      </nav>

      <main>{children}</main>
    </div>
  );
}