import { useAuth } from "../context/AuthContext";

export default function Profile() {
  const { user } = useAuth();

  return (
    <div className="p-6 max-w-md mx-auto">
      <h1 className="text-xl font-bold text-slate-800 mb-6">Profil Saya</h1>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-14 h-14 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xl font-bold">
            {user?.name?.charAt(0).toUpperCase()}
          </div>
          <div>
            <p className="font-medium text-slate-800">{user?.name}</p>
            <span className="inline-block mt-1 px-2 py-0.5 bg-slate-100 text-slate-600 text-xs rounded-full">
              {user?.role}
            </span>
          </div>
        </div>

        <div className="text-sm text-slate-500 border-t border-slate-100 pt-4">
          <p>Untuk mengubah informasi profil atau password, silakan hubungi PM IT / Administrator.</p>
        </div>
      </div>
    </div>
  );
}