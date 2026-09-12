import Link from "next/link";

const FEATURES = [
  {
    icon: "📄",
    title: "Structured resume parsing",
    body: "Upload a PDF or DOCX resume and get back a clean, validated profile: skills, experience, education, and target role.",
  },
  {
    icon: "🔍",
    title: "Semantic job matching",
    body: "Your profile is embedded and matched against a job corpus by meaning, not keywords, using pgvector similarity search.",
  },
  {
    icon: "✏️",
    title: "CV suggestions & rewrite",
    body: "Get actionable, job-specific improvement suggestions and a tailored resume rewrite grounded only in facts already on your CV.",
  },
  {
    icon: "🤖",
    title: "AI Career Mentor",
    body: "Ask career questions and get answers grounded in a curated knowledge base via retrieval-augmented generation — with sources cited.",
  },
];

export default function Home() {
  return (
    <div className="mx-auto max-w-5xl px-6 py-20">
      <div className="text-center">
        <span className="inline-block rounded-full bg-indigo-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-indigo-700">
          Generative AI Career Portal
        </span>
        <h1 className="mt-6 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          SmartHire <span className="text-indigo-600">GenAI</span>
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-600">
          Parse your resume, find jobs that actually match your background, get
          AI-generated CV improvements, and chat with an AI career mentor
          grounded in real guidance documents.
        </p>
        <div className="mt-8 flex justify-center gap-4">
          <Link
            href="/signup"
            className="rounded-md bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
          >
            Get started
          </Link>
          <Link
            href="/login"
            className="rounded-md border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            Sign in
          </Link>
        </div>
      </div>

      <div className="mt-20 grid grid-cols-1 gap-6 sm:grid-cols-2">
        {FEATURES.map((f) => (
          <div key={f.title} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="text-2xl">{f.icon}</div>
            <h3 className="mt-3 font-semibold text-slate-900">{f.title}</h3>
            <p className="mt-2 text-sm text-slate-600">{f.body}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
