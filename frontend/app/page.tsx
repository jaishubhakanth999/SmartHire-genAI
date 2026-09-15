import Link from "next/link";

const FEATURES = [
  { icon: "📄", title: "Resume intelligence", body: "Turn PDF or DOCX resumes into a structured, validated career profile." },
  { icon: "🎯", title: "AI job matching", body: "Use Sarvam AI to compare your profile with available opportunities and rank the strongest fits." },
  { icon: "✨", title: "CV copilot", body: "Get job-specific explanations, improvement suggestions, and fact-grounded rewrites." },
  { icon: "🤖", title: "Career mentor", body: "Ask focused career questions and receive practical answers directly from Sarvam AI." },
];

export default function Home() {
  return (
    <main className="min-h-[calc(100vh-64px)] overflow-hidden">
      <section className="relative">
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_20%_10%,#c7d2fe,transparent_28%),radial-gradient(circle_at_85%_20%,#dbeafe,transparent_30%),linear-gradient(180deg,#f8fafc,#eef2ff)]" />
        <div className="mx-auto grid max-w-6xl items-center gap-12 px-6 py-20 lg:grid-cols-[1.15fr_.85fr] lg:py-28">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-white/80 px-4 py-2 text-xs font-bold uppercase tracking-[0.16em] text-indigo-700 shadow-sm">
              <span className="h-2 w-2 rounded-full bg-emerald-500" /> GenAI Career Platform
            </div>
            <h1 className="mt-7 max-w-3xl text-5xl font-black tracking-tight text-slate-950 sm:text-6xl">
              Build a smarter path from <span className="text-indigo-600">resume to opportunity.</span>
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
              SmartHire GenAI combines resume understanding, AI job matching, explainable CV assistance, and a direct Sarvam AI career mentor into one hackathon-ready workflow.
            </p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Link href="/signup" className="rounded-xl bg-indigo-600 px-6 py-3.5 text-center text-sm font-bold text-white shadow-xl shadow-indigo-200 transition hover:-translate-y-0.5 hover:bg-indigo-500">Start matching →</Link>
              <Link href="/login" className="rounded-xl border border-slate-300 bg-white px-6 py-3.5 text-center text-sm font-bold text-slate-700 shadow-sm transition hover:bg-slate-50">Sign in</Link>
            </div>
            <div className="mt-8 flex flex-wrap gap-5 text-xs font-semibold text-slate-500">
              <span>✓ Explainable matches</span><span>✓ Direct Sarvam AI</span><span>✓ Secure auth</span><span>✓ Cloud deployed</span>
            </div>
          </div>

          <div className="rounded-3xl border border-white/80 bg-slate-950 p-5 shadow-2xl shadow-indigo-200/50">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5 text-white">
              <div className="flex items-center justify-between"><span className="text-sm font-bold">SmartHire workspace</span><span className="rounded-full bg-emerald-400/10 px-2.5 py-1 text-xs text-emerald-300">AI ready</span></div>
              <div className="mt-6 rounded-2xl bg-white p-5 text-slate-900">
                <div className="text-xs font-bold uppercase tracking-wider text-indigo-600">Top match</div>
                <div className="mt-2 flex items-center justify-between gap-4"><div><div className="font-bold">Data Analyst</div><div className="text-sm text-slate-500">Skills aligned with your profile</div></div><div className="rounded-full bg-indigo-50 px-3 py-1 text-sm font-bold text-indigo-700">92%</div></div>
                <div className="mt-5 h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full w-[92%] rounded-full bg-indigo-600" /></div>
              </div>
              <div className="mt-3 grid grid-cols-2 gap-3 text-xs"><div className="rounded-xl bg-white/10 p-4"><div className="text-slate-400">Resume</div><div className="mt-1 font-bold">Structured ✓</div></div><div className="rounded-xl bg-white/10 p-4"><div className="text-slate-400">Mentor</div><div className="mt-1 font-bold">Sarvam ✓</div></div></div>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 pb-20">
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((feature) => (
            <div key={feature.title} className="group rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-indigo-200 hover:shadow-xl hover:shadow-indigo-100/50">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-50 text-xl">{feature.icon}</div>
              <h2 className="mt-5 font-bold text-slate-950">{feature.title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">{feature.body}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
