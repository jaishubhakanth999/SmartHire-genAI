"use client";

import { useState } from "react";
import ResumeUploader from "@/components/ResumeUploader";
import JobMatchCard from "@/components/JobMatchCard";
import type { JobMatch, ResumeRecord } from "@/types";

export default function DashboardPage() {
  const [resume, setResume] = useState<ResumeRecord | null>(null);
  const [matches, setMatches] = useState<JobMatch[]>([]);

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <h1 className="text-2xl font-bold text-slate-900">📄 Resume Matching</h1>
      <p className="mt-1 text-sm text-slate-500">
        Upload your resume to see your parsed profile and matching jobs.
      </p>

      <div className="mt-6">
        <ResumeUploader
          onParsed={(r, m) => {
            setResume(r);
            setMatches(m);
          }}
        />
      </div>

      {resume && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-slate-900">Parsed Profile</h2>
          <div className="mt-3 grid grid-cols-1 gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:grid-cols-2">
            <div className="space-y-1 text-sm">
              <p>
                <span className="font-medium text-slate-700">Name:</span>{" "}
                {resume.parsed.name || "—"}
              </p>
              <p>
                <span className="font-medium text-slate-700">Email:</span>{" "}
                {resume.parsed.email || "—"}
              </p>
              <p>
                <span className="font-medium text-slate-700">Phone:</span>{" "}
                {resume.parsed.phone || "—"}
              </p>
              <p>
                <span className="font-medium text-slate-700">Target role:</span>{" "}
                {resume.parsed.target_role || "—"}
              </p>
            </div>
            <div className="text-sm">
              <p className="font-medium text-slate-700">Skills</p>
              <div className="mt-1 flex flex-wrap gap-1.5">
                {(resume.parsed.skills || []).map((s) => (
                  <span key={s} className="rounded-full bg-indigo-50 px-2 py-0.5 text-xs text-indigo-700">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <details className="mt-3 rounded-lg border border-slate-200 bg-white p-4 text-sm">
            <summary className="cursor-pointer font-medium text-slate-700">
              Full parsed JSON (experience, education…)
            </summary>
            <pre className="mt-3 overflow-x-auto rounded bg-slate-900 p-3 text-xs text-slate-100">
              {JSON.stringify(resume.parsed, null, 2)}
            </pre>
          </details>
        </div>
      )}

      {matches.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-slate-900">Matched Jobs</h2>
          <div className="mt-3 space-y-3">
            {matches.map((job, i) => (
              <JobMatchCard key={job.id} job={job} resumeId={resume!.id} rank={i} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
