interface PreviewModalProps {
  url: string;
  contentType: string;
  filename: string;
  onClose: () => void;
}

export default function PreviewModal({
  url,
  contentType,
  filename,
  onClose,
}: PreviewModalProps) {
  return (
    <div
      className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg max-w-3xl max-h-[85vh] w-full overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
          <span className="text-sm font-medium text-slate-700 truncate">
            {filename}
          </span>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 text-xl leading-none"
          >
            &times;
          </button>
        </div>

        <div className="flex-1 overflow-auto flex items-center justify-center bg-slate-50 p-4">
          {contentType === "application/pdf" ? (
            <iframe src={url} title={filename} className="w-full h-[70vh]" />
          ) : (
            <img
              src={url}
              alt={filename}
              className="max-w-full max-h-full object-contain"
            />
          )}
        </div>
      </div>
    </div>
  );
}
