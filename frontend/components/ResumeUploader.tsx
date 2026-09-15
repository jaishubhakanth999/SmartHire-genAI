"use client";

import { useRef, useState } from "react";
import { apiPostForm } from "@/lib/api";
import type { JobMatch, ResumeRecord } from "@/types";

const MAX_FILE_SIZE = 10 * 1024 * 1024;

export default function ResumeUploader({ onParsed }: { onParsed: (resume: ResumeRecord, matches: JobMatch[]) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(file: File) {
    setError(null);
    const extension = file.name.toLowerCase().split(".").pop() || "";
    if (!extension || !["pdf", "docx"].includes(extension)) {
      setError("Please choose a PDF or DOCX resume.");
      return;
    }
    if (file.size === 0) {
      setError("The selected file is empty.");
      return;
    }
    if (file.size > MAX_FILE_SIZE) {
      setError("Please choose a resume smaller than 10 MB.");
      return;
    }

    setFileName(file.name);
    setUploading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const data = await apiPostForm("/api/resumes", form);
      onParsed(data.resume, data.matches || []);
    } catch (e) {
      setError((e as Error).message || "Could not process this resume.");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      <div
        role="button"
        tabIndex={0}
        aria-label="Upload resume"
        onKeyDown={(e) => { if ((e.key === "Enter" || e.key === " ") && !uploading) inputRef.current?.click(); }}
        onClick={() => !uploading && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); if (!uploading) e.dataTransfer.dropEffect = "copy"; }}
        onDrop={(e) => { e.preventDefault(); const file = e.dataTransfer.files?.[0]; if (file && !uploading) void handleFile(file); }}
        className={`group flex min-h-64 cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-10 text-center transition ${uploading ? "cursor-wait border-indigo-300 bg-indigo-50/50" : "border-slate-300 bg-slate-50/60 hover:border-indigo-400 hover:bg-indigo-50/40"}`}
      >
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white text-3xl shadow-sm ring-1 ring-slate-200 group-hover:scale-105">{uploading ? "⏳" : "📄"}</div>
        <p className="mt-5 text-base font-bold text-slate-800">{uploading ? "Analyzing your resume…" : fileName || "Drop your resume here"}</p>
        <p className="mt-2 text-sm text-slate-500">{uploading ? "Sarvam is extracting and validating your profile" : "or click to browse · PDF or DOCX · up to 10 MB"}</p>
        <input ref={inputRef} type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" className="hidden" onChange={(e) => { const file = e.target.files?.[0]; if (file) void handleFile(file); e.currentTarget.value = ""; }} />
      </div>
      {error && <div role="alert" className="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{error}</div>}
    </div>
  );
}
