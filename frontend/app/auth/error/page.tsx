import Link from "next/link";

export default async function AuthErrorPage({
  searchParams,
}: {
  searchParams: Promise<{ reason?: string }>;
}) {
  const params = await searchParams;
  const expired = params.reason === "invalid-or-expired-token";

  return (
    <main className="flex min-h-[calc(100vh-64px)] items-center justify-center px-6 py-16">
      <div className="w-full max-w-lg rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-xl shadow-slate-200/50">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-50 text-2xl">!</div>
        <h1 className="mt-5 text-2xl font-bold text-slate-950">Verification link unavailable</h1>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          {expired
            ? "This verification link is invalid or has expired. Start again from the sign-up page to request a fresh email."
            : "The verification request was incomplete. Please start again from the sign-up page."}
        </p>
        <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Link href="/signup" className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-500">
            Back to sign up
          </Link>
          <Link href="/login" className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
            Sign in
          </Link>
        </div>
      </div>
    </main>
  );
}
