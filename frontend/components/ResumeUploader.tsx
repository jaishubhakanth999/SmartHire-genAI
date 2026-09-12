"use client";

import { useRef, useState } from "react";
import { apiPostForm } from "@/lib/api";
import type { JobMatch, ResumeRecord } from "@/types";

export default function ResumeUploader({
  onParsed,
}: {
  onParsed: (resume: ResumeRecord, matches: JobMatch[]) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(file: File) {
    setFileName(file.name);
    setUploading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const data = await apiPostForm("/api/resumes", form);
      onParsed(data.resume, data.matches);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          const file = e.dataTransfer.files?.[0];
          if (file) handleFile(file);
        }}
        className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 bg-white px-6 py-10 text-center hover:border-indigo-400"
      >
        <span className="text-3xl">📄</span>
        <p className="text-sm font-medium text-slate-700">
          {fileName ? fileName : "Click or drag a resume here (PDF or DOCX)"}
        </p>
        <p className="text-xs text-slate-400">Processed by the backend, nothing is stored beyond your account&apos;s data</p>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
          }}
        />
      </div>

      {uploading && <p className="mt-3 text-sm text-indigo-600">Parsing resume with the LLM…</p>}
      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
    </div>
  );
}
