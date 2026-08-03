import { useEffect, useState, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";
import {
  createComment,
  deleteComment,
  getComments,
  updateComment,
} from "../api/comments";
import type { Comment } from "../types";

export default function CommentSection({ ticketId }: { ticketId: number }) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newContent, setNewContent] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editContent, setEditContent] = useState("");
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  const fetchComments = async () => {
    setLoading(true);
    try {
      const data = await getComments(ticketId);
      setComments(data);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    fetchComments();
  }, [ticketId]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!newContent.trim()) return;
    await createComment(ticketId, newContent);
    setNewContent("");
    fetchComments;
  };
  const handleUpdate = async (commentId: number) => {
    if (!editContent.trim()) return;
    await updateComment(ticketId, commentId, editContent);
    setEditingId(null);
    fetchComments();
  };
  const handleDelete = async (commentId: number) => {
    if (!confirm("Hapus komentar ini?")) return;
    await deleteComment(ticketId, commentId);
    fetchComments();
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="mb-4">
        <textarea
          value={newContent}
          onChange={(e) => setNewContent(e.target.value)}
          placeholder="Tulis komentar..."
          rows={3}
          className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="mt-2 bg-blue-600 text-white px-4 py-1.5 rounded-md text-sm font-medium hover:bg-blue-700"
        >
          Kirim
        </button>
      </form>

      {loading ? (
        <p className="text-sm text-slate-400">Memuat komentar...</p>
      ) : comments.length === 0 ? (
        <p className="text-sm text-slate-400">Belum ada komentar.</p>
      ) : (
        <div className="space-y-3">
          {comments.map((c) => {
            const isOwner = user?.id === c.author.id;
            return (
              <div
                key={c.id}
                className="border border-slate-200 rounded-md p-3"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-slate-700">
                    {c.author.name}
                  </span>
                  <span className="text-xs text-slate-400">
                    {new Date(c.created_at).toLocaleString("id-ID")}
                  </span>
                </div>

                {editingId === c.id ? (
                  <div>
                    <textarea
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      rows={2}
                      className="w-full px-2 py-1 border border-slate-300 rounded text-sm"
                    />
                    <div className="flex gap-2 mt-1">
                      <button
                        onClick={() => handleUpdate(c.id)}
                        className="text-xs text-blue-600 font-medium"
                      >
                        Simpan
                      </button>
                      <button
                        onClick={() => setEditingId(null)}
                        className="text-xs text-slate-500"
                      >
                        Batal
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <p className="text-sm text-slate-600">{c.content}</p>
                    {isOwner && (
                      <div className="flex gap-3 mt-1">
                        <button
                          onClick={() => {
                            setEditingId(c.id);
                            setEditContent(c.content);
                          }}
                          className="text-xs text-slate-500 hover:text-blue-600"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(c.id)}
                          className="text-xs text-slate-500 hover:text-red-600"
                        >
                          Hapus
                        </button>
                      </div>
                    )}
                  </>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
