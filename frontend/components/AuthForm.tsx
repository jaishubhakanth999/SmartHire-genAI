"use client";

import { useState, type FormEvent } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";

const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL ||
  (process.env.NEXT_PUBLIC_VERCEL_URL ? `https://${process.env.NEXT_PUBLIC_VERCEL_URL}` : "https://smart-hire-gen-ai-swart.vercel.app");

export default function AuthForm({ mode }: { mode: "login" | "signup" }) {
  const router = useRouter();
  const params = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setNotice(null);
    const supabase = createClient();

    if (mode === "signup") {
      const { data, error } = await supabase.auth.signUp({
        email: email.trim().toLowerCase(),
        password,
        options: {
          data: { full_name: fullName.trim() },
          emailRedirectTo: `${SITE_URL}/auth/confirm?next=/dashboard`,
        },
      });
      setLoading(false);
      if (error) {
        setError(error.message);
        return;
      }
      if (data.session) {
        router.push("/dashboard");
        router.refresh();
        return;
      }
      setNotice("Account created. Check your email and click the verification link before signing in.");
      return;
    }

    const { data, error } = await supabase.auth.signInWithPassword({
      email: email.trim().toLowerCase(),
      password,
    });
    setLoading(false);
    if (error) {
      setError(error.message);
      return;
    }
    if (!data.user?.email_confirmed_at) {
      await supabase.auth.signOut();
      setError("Please verify your email address before signing in.");
      return;
    }
    const redirect = params.get("redirect");
    router.push(redirect?.startsWith("/") ? redirect : "/dashboard");
    router.refresh();
  }

  return (
    <main className="relative flex min-h-[calc(100vh-64px)] items-center justify-center overflow-hidden px-6 py-14">
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top,#e0e7ff,transparent_42%),linear-gradient(180deg,#f8fafc,#eef2ff)]" />
      <div className="grid w-full max-w-5xl overflow-hidden rounded-3xl border border-white/70 bg-white/90 shadow-2xl shadow-indigo-200/40 backdrop-blur md:grid-cols-2">
        <section className="hidden bg-slate-950 p-10 text-white md:flex md:flex-col md:justify-between">
          <div>
            <div className="flex items-center gap-3 text-lg font-bold"><span className="rounded-xl bg-indigo-500/20 p-2">🎯</span> SmartHire GenAI</div>
            <h2 className="mt-16 text-4xl font-bold leading-tight">Turn a resume into a career plan.</h2>
            <p className="mt-5 max-w-sm text-sm leading-6 text-slate-300">Semantic job matching, evidence-grounded CV help, and a focused AI career mentor in one workflow.</p>
          </div>
          <p className="text-xs text-slate-500">Secure authentication powered by Supabase</p>
        </section>

        <section className="p-7 sm:p-10">
          <div className="mb-7">
            <span className="text-xs font-bold uppercase tracking-[0.18em] text-indigo-600">SmartHire</span>
            <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
              {mode === "login" ? "Welcome back" : "Create your account"}
            </h1>
            <p className="mt-2 text-sm text-slate-500">
              {mode === "login" ? "Sign in to continue your career journey." : "Verify your email to unlock your personalized workspace."}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === "signup" && (
              <div>
                <label htmlFor="fullName" className="block text-sm font-semibold text-slate-700">Full name</label>
                <input id="fullName" type="text" required value={fullName} onChange={(e) => setFullName(e.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100" placeholder="Your name" />
              </div>
            )}
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-slate-700">Email</label>
              <input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100" placeholder="you@example.com" />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-slate-700">Password</label>
              <input id="password" type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100" placeholder="At least 8 characters" />
            </div>

            {error && <div role="alert" className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>}
            {notice && <div role="status" className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{notice}</div>}

            <button type="submit" disabled={loading} className="w-full rounded-xl bg-indigo-600 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-indigo-200 transition hover:bg-indigo-500 hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60">
              {loading ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500">
            {mode === "login" ? <>No account? <Link href="/signup" className="font-bold text-indigo-600 hover:underline">Create one</Link></> : <>Already registered? <Link href="/login" className="font-bold text-indigo-600 hover:underline">Sign in</Link></>}
          </p>
        </section>
      </div>
    </main>
  );
}
