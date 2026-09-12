"use client";

import { useEffect, useState } from "react";
import { apiDelete, apiGet, apiPostJson } from "@/lib/api";

type AdminJob = {
  id: string;
  title: string;
  company: string | null;
  skills: string | null;
  description: string;
};

export default function AdminJobsPanel() {
  const [jobs, setJobs] = useState<AdminJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ title: "", company: "", skills: "", description: "" });
  const [submitting, setSubmitting] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const data = await apiGet("/api/admin/jobs");
      setJobs(data.jobs);
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
    apiGet("/api/admin/jobs")
      .then((data) => setJobs(data.jobs))
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false));
  }, []);

  async function addJob(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await apiPostJson("/api/admin/jobs", form);
      setForm({ title: "", company: "", skills: "", description: "" });
      await load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  async function removeJob(id: string) {
    try {
      await apiDelete(`/api/admin/jobs/${id}`);
      setJobs((prev) => prev.filter((j) => j.id !== id));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-slate-900">Job corpus ({jobs.length})</h2>
      <p className="mt-1 text-sm text-slate-500">
        Jobs are embedded on save and become searchable immediately via pgvector.
      </p>

      <form onSubmit={addJob} className="mt-4 grid grid-cols-1 gap-3 rounded-xl border border-slate-200 bg-white p-4 sm:grid-cols-2">
        <input
          required
          placeholder="Title"
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
        <input
          placeholder="Company"
          value={form.company}
          onChange={(e) => setForm({ ...form, company: e.target.value })}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
        <input
          placeholder="Skills (comma-separated)"
          value={form.skills}
          onChange={(e) => setForm({ ...form, skills: e.target.value })}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm sm:col-span-2"
        />
        <textarea
          required
          placeholder="Description"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm sm:col-span-2"
          rows={3}
        />
        <button
          type="submit"
          disabled={submitting}
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50 sm:col-span-2"
        >
          {submitting ? "Embedding…" : "Add job"}
        </button>
      </form>

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

      <div className="mt-4 space-y-2">
        {loading ? (
          <p className="text-sm text-slate-400">Loading…</p>
        ) : (
          jobs.map((j) => (
            <div key={j.id} className="flex items-start justify-between rounded-lg border border-slate-200 bg-white p-3 text-sm">
              <div>
                <p className="font-medium text-slate-800">
                  {j.title} {j.company && <span className="text-slate-400">@ {j.company}</span>}
                </p>
                {j.skills && <p className="text-xs text-slate-500">{j.skills}</p>}
              </div>
              <button onClick={() => removeJob(j.id)} className="text-xs font-medium text-red-600 hover:text-red-500">
                Delete
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
