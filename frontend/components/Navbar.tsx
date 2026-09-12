"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { useProfile } from "@/lib/useProfile";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { profile } = useProfile();

  async function signOut() {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/login");
    router.refresh();
  }

  const links = [
    { href: "/dashboard", label: "Resume Matching" },
    { href: "/mentor", label: "Career Mentor" },
    ...(profile?.role === "admin" ? [{ href: "/admin", label: "Admin" }] : []),
  ];

  return (
    <header className="border-b border-slate-200 bg-white/80 backdrop-blur sticky top-0 z-10">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        <Link href="/" className="flex items-center gap-2 font-semibold text-slate-900">
          <span className="text-xl">🎯</span>
          SmartHire GenAI
        </Link>

        {profile && (
          <nav className="hidden gap-6 text-sm font-medium text-slate-600 sm:flex">
            {links.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                className={
                  pathname?.startsWith(l.href)
                    ? "text-indigo-600"
                    : "hover:text-slate-900 transition-colors"
                }
              >
                {l.label}
              </Link>
            ))}
          </nav>
        )}

        <div className="flex items-center gap-3">
          {profile ? (
            <>
              <span className="hidden text-sm text-slate-500 sm:inline">
                {profile.email} {profile.role === "admin" && <span className="ml-1 rounded bg-indigo-100 px-1.5 py-0.5 text-xs font-medium text-indigo-700">admin</span>}
              </span>
              <button
                onClick={signOut}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="text-sm font-medium text-slate-700 hover:text-slate-900">
                Sign in
              </Link>
              <Link
                href="/signup"
                className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-500"
              >
                Sign up
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
