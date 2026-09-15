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
    { href: "/dashboard", label: "Resume Match", icon: "🎯" },
    { href: "/mentor", label: "AI Mentor", icon: "🤖" },
    ...(profile?.role === "admin" ? [{ href: "/admin", label: "Admin", icon: "⚙️" }] : []),
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/85 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-5 sm:px-6">
        <Link href="/" className="flex items-center gap-2.5 text-sm font-black tracking-tight text-slate-950">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 text-base text-white shadow-lg shadow-indigo-200">🎯</span>
          <span>SmartHire <span className="text-indigo-600">GenAI</span></span>
        </Link>

        {profile && (
          <nav className="hidden items-center gap-1 rounded-xl bg-slate-100 p-1 md:flex">
            {links.map((link) => {
              const active = pathname?.startsWith(link.href);
              return <Link key={link.href} href={link.href} className={`rounded-lg px-3 py-2 text-xs font-bold transition ${active ? "bg-white text-indigo-700 shadow-sm" : "text-slate-500 hover:text-slate-900"}`}><span className="mr-1">{link.icon}</span>{link.label}</Link>;
            })}
          </nav>
        )}

        <div className="flex items-center gap-2.5">
          {profile ? (
            <>
              <span className="hidden max-w-44 truncate rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 sm:block">{profile.full_name || profile.email}</span>
              <button onClick={signOut} className="rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-xs font-bold text-slate-700 transition hover:bg-slate-50">Sign out</button>
            </>
          ) : (
            <>
              <Link href="/login" className="rounded-xl px-3 py-2 text-xs font-bold text-slate-600 hover:text-slate-950">Sign in</Link>
              <Link href="/signup" className="rounded-xl bg-indigo-600 px-3.5 py-2 text-xs font-bold text-white shadow-lg shadow-indigo-200 hover:bg-indigo-500">Get started</Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
