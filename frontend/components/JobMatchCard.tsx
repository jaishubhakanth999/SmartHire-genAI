"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { apiPostJson } from "@/lib/api";
import type { JobMatch } from "@/types";

type ActionKind = "explain" | "suggestions" | "rewrite";

const ACTION_LABEL: Record<ActionKind, string> = {
  explain: "💡 Explain this match",
  suggestions: "✏️ CV improvement suggestions",
  rewrite: "🔄 Rewrite my resume for this job",
};

export default function JobMatchCard({ job, resumeId, rank }: { job: JobMatch; resumeId: string; rank: number }) {
  const [open, setOpen] = useState(rank === 0);
  const [loadingAction, setLoadingAction] = useState<ActionKind | null>(null);
  const [results, setResults] = useState<Partial<Record<ActionKind, string>>>({});

  async function runAction(kind: ActionKind) {
    setLoadingAction(kind);
    try {
      const data = await apiPostJson(`/api/cv/${kind}`, { resume_id: resumeId, job_id: job.id });
      setResults((prev) => ({ ...prev, [kind]: data.content }));
    } catch (e) {
      setResults((prev) => ({ ...prev, [kind]: `Error: ${(e as Error).message}` }));
    } finally {
      setLoadingAction(null);
    }
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
      >
        <div>
          <div className="flex items-center gap-2">
            {rank === 0 && <span>🥇</span>}
            <span className="font-semibold text-slate-900">{job.title}</span>
            <span className="text-slate-400">@</span>
            <span className="text-slate-600">{job.company}</span>
          </div>
          {job.skills && <div className="mt-1 text-xs text-slate-500">{job.skills}</div>}
        </div>
        <span className="shrink-0 rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-700">
          {Math.round(job.similarity * 100)}% match
        </span>
      </button>

      {open && (
        <div className="border-t border-slate-100 px-5 py-4">
          <p className="text-sm text-slate-600">{job.description}</p>

          <div className="mt-4 flex flex-wrap gap-2">
            {(Object.keys(ACTION_LABEL) as ActionKind[]).map((kind) => (
              <button
                key={kind}
                onClick={() => runAction(kind)}
                disabled={loadingAction !== null}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
              >
                {loadingAction === kind ? "Working…" : ACTION_LABEL[kind]}
              </button>
            ))}
          </div>

          {(Object.keys(results) as ActionKind[]).map(
            (kind) =>
              results[kind] && (
                <div key={kind} className="mt-4 rounded-lg bg-slate-50 p-4 text-sm">
                  <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                    {ACTION_LABEL[kind]}
                  </div>
                  <div className="prose prose-sm max-w-none prose-slate">
                    <ReactMarkdown>{results[kind]}</ReactMarkdown>
                  </div>
                </div>
              )
          )}
        </div>
      )}
    </div>
  );
}
