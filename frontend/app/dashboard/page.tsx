"use client";

import { useEffect, useState } from "react";
import ResumeUploader from "@/components/ResumeUploader";
import JobMatchCard from "@/components/JobMatchCard";
import { apiDelete, apiGet } from "@/lib/api";
import type { JobMatch, ResumeRecord } from "@/types";

export default function DashboardPage() {
  const [resume, setResume] = useState<ResumeRecord | null>(null);
  const [matches, setMatches] = useState<JobMatch[]>([]);
  const [history, setHistory] = useState<ResumeRecord[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [loadingMatches, setLoadingMatches] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadHistory(selectLatest = true) {
    setLoadingHistory(true);
    setError(null);
    try {
      const data = await apiGet("/api/resumes");
      const resumes = (data.resumes || []) as ResumeRecord[];
      setHistory(resumes);
      if (selectLatest && resumes[0]) await selectResume(resumes[0]);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoadingHistory(false);
    }
  }

  async function selectResume(item: ResumeRecord) {
    setResume(item);
    setLoadingMatches(true);
    setError(null);
    try {
      const data = await apiGet(`/api/resumes/${item.id}/matches`);
      setMatches((data.matches || []) as JobMatch[]);
    } catch (e) {
      setMatches([]);
      setError((e as Error).message);
    } finally {
      setLoadingMatches(false);
    }
  }

  useEffect(() => {
    void loadHistory();
  }, []);

  async function removeResume(id: string) {
    setError(null);
    try {
      await apiDelete(`/api/resumes/${id}`);
      const remaining = history.filter((item) => item.id !== id);
      setHistory(remaining);
      if (resume?.id === id) {
        setResume(null);
        setMatches([]);
        if (remaining[0]) await selectResume(remaining[0]);
      }
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <main className="min-h-[calc(100vh-64px)] bg-slate-50/70">
      <div className="mx-auto max-w-6xl px-5 py-8 sm:px-6 sm:py-10">
        <div className="rounded-3xl bg-slate-950 p-7 text-white shadow-2xl shadow-indigo-100 sm:p-10">
          <div className="max-w-3xl">
            <div className="text-xs font-bold uppercase tracking-[0.18em] text-indigo-300">Career workspace</div>
            <h1 className="mt-3 text-3xl font-black tracking-tight sm:text-4xl">Find where your resume fits best.</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">Upload your resume and SmartHire will structure your profile, rank relevant opportunities, and give you explainable CV actions.</p>
          </div>
          <div className="mt-7 grid gap-3 sm:grid-cols-3">
            {["1. Upload resume", "2. Understand profile", "3. Match + improve"].map((item) => <div key={item} className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-xs font-semibold text-slate-200">{item}</div>)}
          </div>
        </div>

        {error && <div role="alert" className="mt-5 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{error}</div>}

        <div className="mt-6 grid gap-6 lg:grid-cols-[300px_1fr]">
          <aside className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div><div className="text-xs font-bold uppercase tracking-wider text-indigo-600">My resumes</div><h2 className="mt-1 text-lg font-black text-slate-950">Saved history</h2></div>
              <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-bold text-slate-600">{history.length}</span>
            </div>
            <div className="mt-4 space-y-2">
              {loadingHistory ? <p className="text-sm text-slate-400">Loading…</p> : history.length === 0 ? <p className="text-sm leading-6 text-slate-400">Your uploaded resumes will appear here.</p> : history.map((item) => (
                <div key={item.id} className={`rounded-2xl border p-3 ${resume?.id === item.id ? "border-indigo-200 bg-indigo-50/60" : "border-slate-200 bg-white"}`}>
                  <button className="w-full text-left" onClick={() => void selectResume(item)}>
                    <div className="truncate text-sm font-bold text-slate-800">{item.filename}</div>
                    <div className="mt-1 text-xs text-slate-400">{new Date(item.created_at).toLocaleString()}</div>
                  </button>
                  <button onClick={() => void removeResume(item.id)} className="mt-2 text-xs font-semibold text-rose-600 hover:text-rose-500">Delete</button>
                </div>
              ))}
            </div>
          </aside>

          <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7">
            <ResumeUploader onParsed={(r, m) => { setResume(r); setMatches(m); setHistory((prev) => [r, ...prev.filter((x) => x.id !== r.id)]); }} />
          </section>
        </div>

        {resume && (
          <section className="mt-7">
            <div className="mb-3 flex items-end justify-between"><div><div className="text-xs font-bold uppercase tracking-wider text-indigo-600">Profile intelligence</div><h2 className="mt-1 text-xl font-black text-slate-950">What we found</h2></div><span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">Resume parsed ✓</span></div>
            <div className="grid gap-5 lg:grid-cols-[1fr_.8fr]">
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="grid gap-4 sm:grid-cols-2 text-sm">
                  {[['Name', resume.parsed.name], ['Email', resume.parsed.email], ['Phone', resume.parsed.phone], ['Target role', resume.parsed.target_role]].map(([label, value]) => <div key={label as string}><div className="text-xs font-bold uppercase tracking-wide text-slate-400">{label}</div><div className="mt-1 font-semibold text-slate-800">{value || 'Not detected'}</div></div>)}
                </div>
                {resume.parsed.experience?.length > 0 && <div className="mt-6"><div className="text-xs font-bold uppercase tracking-wide text-slate-400">Experience</div><div className="mt-3 space-y-2">{resume.parsed.experience.slice(0, 4).map((item, i) => <div key={i} className="rounded-xl bg-slate-50 p-3 text-sm"><div className="font-bold text-slate-800">{item.title}</div><div className="text-slate-500">{item.company}{item.start_date ? ` · ${item.start_date}` : ""}{item.end_date ? `–${item.end_date}` : ""}</div></div>)}</div></div>}
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"><div className="text-xs font-bold uppercase tracking-wide text-slate-400">Detected skills</div><div className="mt-3 flex flex-wrap gap-2">{(resume.parsed.skills || []).map((skill) => <span key={skill} className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">{skill}</span>)}</div><div className="mt-6 text-xs font-bold uppercase tracking-wide text-slate-400">Education</div><div className="mt-3 space-y-2">{(resume.parsed.education || []).slice(0, 4).map((item, i) => <div key={i} className="rounded-xl bg-slate-50 p-3 text-sm"><div className="font-bold text-slate-800">{item.degree}</div><div className="text-slate-500">{item.institution}{item.year ? ` · ${item.year}` : ""}</div></div>)}</div></div>
            </div>
          </section>
        )}

        {resume && <section className="mt-8"><div className="mb-4"><div className="text-xs font-bold uppercase tracking-wider text-indigo-600">Opportunity ranking</div><h2 className="mt-1 text-2xl font-black text-slate-950">Best matches for you</h2><p className="mt-1 text-sm text-slate-500">Each match can be explained and turned into a concrete CV improvement.</p></div>{loadingMatches ? <div className="rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-400">Refreshing your matches…</div> : matches.length === 0 ? <div className="rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-500">No matching opportunities were found yet.</div> : <div className="space-y-3">{matches.map((job, i) => <JobMatchCard key={job.id} job={job} resumeId={resume.id} rank={i} />)}</div>}</section>}
      </div>
    </main>
  );
}
