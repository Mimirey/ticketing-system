import { useState, useEffect, useRef } from "react";
import {
  getAttachments, uploadAttachment, deleteAttachment, downloadAttachment, getAttachmentPreviewUrl, PREVIEWABLE_TYPES
} from "../api/attachments";
import type { Attachment } from "../types";
import PreviewModal from "./PreviewModal";
import ConfirmModal from "./ConfirModal";

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function AttachmentSection({ ticketId }: { ticketId: number }) {
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<{ url: string; type: string; filename: string } | null>(null);
  const fetchAttachments = async () => {
    setLoading(true);
    try {
      const data = await getAttachments(ticketId);
      setAttachments(data);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    fetchAttachments();
  }, [ticketId]);
  const [attachmentToDelete, setAttachmentToDelete] = useState<Attachment | null>(null);
    const confirmDeleteAttachment = async () => {
    if (!attachmentToDelete) return;
    await deleteAttachment(ticketId, attachmentToDelete.id);
    setAttachmentToDelete(null);
    fetchAttachments();
    };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setError(null);
    setUploading(true);
    try {
      await uploadAttachment(ticketId, file);
      fetchAttachments();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Gagal mengunggah file");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };
  const handlePreview = async (a: Attachment) => {
    const url = await getAttachmentPreviewUrl(ticketId, a.id);
    setPreview({ url, type: a.content_type, filename: a.original_filename });
  };
  const closePreview = () => {
    if (preview) window.URL.revokeObjectURL(preview.url);
    setPreview(null);
  };
  return (
    <div>
      <div className="mb-4">
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileChange}
          disabled={uploading}
          accept=".png,.jpg,.jpeg,.pdf,.doc,.docx,.xls,.xlsx"
          className="text-sm"
        />
        {uploading && (
          <p className="text-xs text-slate-400 mt-1">Mengunggah...</p>
        )}
        {error && <p className="text-xs text-red-600 mt-1">{error}</p>}
      </div>

      {loading ? (
        <p className="text-sm text-slate-400">Memuat lampiran...</p>
      ) : attachments.length === 0 ? (
        <p className="text-sm text-slate-400">Belum ada lampiran.</p>
      ) : (
        <div className="space-y-2">
          {attachments.map((a) => (
            <div
              key={a.id}
              className="flex items-center justify-between border border-slate-200 rounded-md p-3"
            >
              <div>
                <p className="text-sm font-medium text-slate-700">
                  {a.original_filename}
                </p>
                <p className="text-xs text-slate-400">
                  {formatFileSize(a.file_size)} · diunggah oleh{" "}
                  {a.uploaded_by.name}
                </p>
              </div>
              <div className="flex gap-3">
                {PREVIEWABLE_TYPES.includes(a.content_type) && (
                  <button onClick={() => handlePreview(a)} className="text-xs text-slate-600 font-medium hover:text-slate-800">
                    Preview
                  </button>
                )}
                <button
                  onClick={() =>
                    downloadAttachment(ticketId, a.id, a.original_filename)
                  }
                  className="text-xs text-blue-600 font-medium"
                >
                  Unduh
                </button>
                <button
                  onClick={() => setAttachmentToDelete(a)}
                  className="text-xs text-red-600 font-medium"
                >
                  Hapus
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      {preview && (
        <PreviewModal
          url={preview.url}
          contentType={preview.type}
          filename={preview.filename}
          onClose={closePreview}
        />
      )}
      {attachmentToDelete && (
        <ConfirmModal
            title="Hapus Lampiran"
            message={`Yakin ingin menghapus "${attachmentToDelete.original_filename}"?`}
            onConfirm={confirmDeleteAttachment}
            onCancel={() => setAttachmentToDelete(null)}
        />
        )}
    </div>
  );
}
