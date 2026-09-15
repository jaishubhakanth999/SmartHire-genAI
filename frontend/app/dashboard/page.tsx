"use client";

import { useState } from "react";
import ResumeUploader from "@/components/ResumeUploader";
import JobMatchCard from "@/components/JobMatchCard";
import type { JobMatch, ResumeRecord } from "@/types";

export default function DashboardPage() {
  const [resume, setResume] = useState<ResumeRecord | null>(null);
  const [matches, setMatches] = useState<JobMatch[]>([]);

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

        <div className="mt-6 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7">
          <ResumeUploader onParsed={(r, m) => { setResume(r); setMatches(m); }} />
        </div>

        {resume && (
          <section className="mt-7">
            <div className="mb-3 flex items-end justify-between"><div><div className="text-xs font-bold uppercase tracking-wider text-indigo-600">Profile intelligence</div><h2 className="mt-1 text-xl font-black text-slate-950">What we found</h2></div><span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">Resume parsed ✓</span></div>
            <div className="grid gap-5 lg:grid-cols-[1fr_.8fr]">
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="grid gap-4 sm:grid-cols-2 text-sm">
                  {[['Name', resume.parsed.name], ['Email', resume.parsed.email], ['Phone', resume.parsed.phone], ['Target role', resume.parsed.target_role]].map(([label, value]) => <div key={label as string}><div className="text-xs font-bold uppercase tracking-wide text-slate-400">{label}</div><div className="mt-1 font-semibold text-slate-800">{value || 'Not detected'}</div></div>)}
                </div>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"><div className="text-xs font-bold uppercase tracking-wide text-slate-400">Detected skills</div><div className="mt-3 flex flex-wrap gap-2">{(resume.parsed.skills || []).map((skill) => <span key={skill} className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">{skill}</span>)}</div></div>
            </div>
          </section>
        )}

        {matches.length > 0 && <section className="mt-8"><div className="mb-4"><div className="text-xs font-bold uppercase tracking-wider text-indigo-600">Opportunity ranking</div><h2 className="mt-1 text-2xl font-black text-slate-950">Best matches for you</h2><p className="mt-1 text-sm text-slate-500">Each match can be explained and turned into a concrete CV improvement.</p></div><div className="space-y-3">{matches.map((job, i) => <JobMatchCard key={job.id} job={job} resumeId={resume!.id} rank={i} />)}</div></section>}
      </div>
    </main>
  );
}
