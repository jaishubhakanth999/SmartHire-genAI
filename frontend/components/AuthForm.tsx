"use client";

import { useState, type FormEvent } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";

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
      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: { data: { full_name: fullName } },
      });
      setLoading(false);
      if (error) {
        setError(error.message);
        return;
      }
      setNotice(
        "Account created. If email confirmation is enabled on your Supabase project, check your inbox before signing in."
      );
      return;
    }

    const { error } = await supabase.auth.signInWithPassword({ email, password });
    setLoading(false);
    if (error) {
      setError(error.message);
      return;
    }
    router.push(params.get("redirect") || "/dashboard");
    router.refresh();
  }

  return (
    <div className="mx-auto flex min-h-[calc(100vh-57px)] max-w-md flex-col justify-center px-6 py-12">
      <div className="mb-8 text-center">
        <div className="text-3xl">🎯</div>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">
          {mode === "login" ? "Sign in" : "Create your account"}
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          {mode === "login" ? "Welcome back to SmartHire GenAI" : "Start matching jobs and chatting with your mentor"}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        {mode === "signup" && (
          <div>
            <label className="block text-sm font-medium text-slate-700">Full name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              placeholder="Ada Lovelace"
            />
          </div>
        )}
        <div>
          <label className="block text-sm font-medium text-slate-700">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            placeholder="you@example.com"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Password</label>
          <input
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            placeholder="••••••••"
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}
        {notice && <p className="text-sm text-green-600">{notice}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-60"
        >
          {loading ? "Please wait…" : mode === "login" ? "Sign in" : "Sign up"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-500">
        {mode === "login" ? (
          <>
            No account?{" "}
            <Link href="/signup" className="font-medium text-indigo-600 hover:text-indigo-500">
              Sign up
            </Link>
          </>
        ) : (
          <>
            Already have an account?{" "}
            <Link href="/login" className="font-medium text-indigo-600 hover:text-indigo-500">
              Sign in
            </Link>
          </>
        )}
      </p>
    </div>
  );
}
