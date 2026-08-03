interface ConfirmModalProps {
  title: string;
  message: string;
  confirmLabel?: string;
  danger?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmModal({
  title,
  message,
  confirmLabel = "Hapus",
  danger = true,
  onConfirm,
  onCancel,
}: ConfirmModalProps) {
  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={onCancel}
    >
      <div
        className="bg-white rounded-lg shadow-xl max-w-sm w-full p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-base font-semibold text-slate-800 mb-2">{title}</h2>
        <p className="text-sm text-slate-500 mb-6">{message}</p>

        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-md"
          >
            Batal
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-2 text-sm font-medium text-white rounded-md ${
              danger ? "bg-red-600 hover:bg-red-700" : "bg-blue-600 hover:bg-blue-700"
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}