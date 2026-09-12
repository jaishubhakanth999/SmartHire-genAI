"use client";

import { useEffect, useState } from "react";
import { apiDelete, apiGet, apiPostJson } from "@/lib/api";

type AdminNote = {
  id: string;
  filename: string;
  chunk_index: number;
  content: string;
};

export default function AdminNotesPanel() {
  const [notes, setNotes] = useState<AdminNote[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ filename: "", content: "" });
  const [submitting, setSubmitting] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const data = await apiGet("/api/admin/career-notes");
      setNotes(data.notes);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // Fetch directly (not via `load()`) so no setState call happens
    // synchronously within the effect body itself -- state updates only
    // happen inside the async callbacks below.
    apiGet("/api/admin/career-notes")
      .then((data) => setNotes(data.notes))
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false));
  }, []);

  async function addNote(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await apiPostJson("/api/admin/career-notes", form);
      setForm({ filename: "", content: "" });
      await load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  async function removeNote(filename: string) {
    try {
      await apiDelete(`/api/admin/career-notes/${encodeURIComponent(filename)}`);
      await load();
    } catch (e) {
      setError((e as Error).message);
    }
  }

  const grouped = notes.reduce<Record<string, AdminNote[]>>((acc, n) => {
    (acc[n.filename] ||= []).push(n);
    return acc;
  }, {});

  return (
    <div>
      <h2 className="text-lg font-semibold text-slate-900">Career notes knowledge base ({Object.keys(grouped).length} documents)</h2>
      <p className="mt-1 text-sm text-slate-500">
        Documents are chunked and embedded on save, and become retrievable by the mentor immediately.
      </p>

      <form onSubmit={addNote} className="mt-4 space-y-3 rounded-xl border border-slate-200 bg-white p-4">
        <input
          required
          placeholder="Filename (e.g. negotiation_tips.txt)"
          value={form.filename}
          onChange={(e) => setForm({ ...form, filename: e.target.value })}
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
        <textarea
          required
          placeholder="Document content"
          value={form.content}
          onChange={(e) => setForm({ ...form, content: e.target.value })}
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          rows={5}
        />
        <button
          type="submit"
          disabled={submitting}
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
        >
          {submitting ? "Chunking + embedding…" : "Add document"}
        </button>
      </form>

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

      <div className="mt-4 space-y-2">
        {loading ? (
          <p className="text-sm text-slate-400">Loading…</p>
        ) : (
          Object.entries(grouped).map(([filename, chunks]) => (
            <div key={filename} className="flex items-start justify-between rounded-lg border border-slate-200 bg-white p-3 text-sm">
              <div>
                <p className="font-medium text-slate-800">{filename}</p>
                <p className="text-xs text-slate-500">{chunks.length} chunk(s)</p>
              </div>
              <button onClick={() => removeNote(filename)} className="text-xs font-medium text-red-600 hover:text-red-500">
                Delete
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
