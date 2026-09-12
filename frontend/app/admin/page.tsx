"use client";

import { useProfile } from "@/lib/useProfile";
import AdminJobsPanel from "@/components/AdminJobsPanel";
import AdminNotesPanel from "@/components/AdminNotesPanel";

export default function AdminPage() {
  const { profile, loading } = useProfile();

  if (loading) {
    return <div className="mx-auto max-w-4xl px-6 py-10 text-sm text-slate-400">Loading…</div>;
  }

  if (!profile || profile.role !== "admin") {
    return (
      <div className="mx-auto max-w-4xl px-6 py-10">
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-6 text-amber-800">
          <h1 className="font-semibold">Admins only</h1>
          <p className="mt-1 text-sm">
            Your account doesn&apos;t have admin access. Ask whoever manages the Supabase project to run:
          </p>
          <pre className="mt-2 overflow-x-auto rounded bg-white p-3 text-xs text-slate-700">
            {`update public.profiles set role = 'admin' where email = 'your-email@example.com';`}
          </pre>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-10 px-6 py-10">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">⚙️ Admin Panel</h1>
        <p className="mt-1 text-sm text-slate-500">Manage the job corpus and the mentor&apos;s knowledge base.</p>
      </div>
      <AdminJobsPanel />
      <AdminNotesPanel />
    </div>
  );
}
