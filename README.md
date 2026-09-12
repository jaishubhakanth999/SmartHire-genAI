# SmartHire GenAI — Resume Matching & AI Career Mentor

A real, three-tier web application: a **Next.js** frontend (deployable to
**Vercel**), a **FastAPI** backend (deployable to **Render**), and
**Supabase** (Postgres + pgvector + Auth) as the database.

1. **Parsed profile** — structured JSON extracted from an uploaded CV by an LLM
2. **Matched jobs** — semantic search over a job corpus via Postgres/pgvector
3. **CV suggestions & rewrite** — LLM-generated, actionable improvement advice and a tailored resume rewrite
4. **AI Career Mentor** — a RAG chatbot grounded in a career-notes knowledge base, with conversation memory and source citations
5. **Admin panel** — manage the job corpus and the mentor's knowledge base from the browser (no CLI needed after setup)

> The previous Streamlit/FAISS prototype is preserved (not deleted) in
> [`legacy/`](legacy/) for reference. It is not part of the running system.

---

## Architecture

```
┌─────────────────┐        ┌──────────────────┐        ┌───────────────────────┐
│  frontend/       │  REST  │  backend/         │  SQL   │  Supabase              │
│  Next.js         │ ─────► │  FastAPI          │ ─────► │  Postgres + pgvector   │
│  (Vercel)        │        │  (Render)         │        │  + Auth                │
│                  │ ◄───── │                   │ ◄───── │                        │
│  Auth via        │  JWT   │  Verifies the     │        │  profiles, resumes,    │
│  supabase-js     │        │  Supabase JWT on  │        │  jobs, career_notes,   │
│  (anon key)      │        │  every request    │        │  chat_sessions/messages│
└─────────────────┘        └──────────────────┘        └───────────────────────┘
```

- The frontend talks to Supabase **directly** only for authentication
  (sign up / sign in / sign out) and for reading the signed-in user's own
  `profiles` row (to know if they're an admin) — both protected by RLS.
- Every other operation (resume upload, job matching, CV suggestions, mentor
  chat, admin CRUD) goes through the **backend**, which uses the Supabase
  **service role key** server-side only.
- Job and career-note **embeddings live in Postgres** via the `pgvector`
  extension — no local FAISS files, no build-index step. Adding a job or a
  career note through the admin panel embeds it immediately.

---

## Repository layout

```
smarthire-genai/
├── frontend/                 Next.js 16 (App Router, TypeScript, Tailwind)
│   ├── app/                  pages: /, /login, /signup, /dashboard, /mentor, /admin
│   ├── components/           Navbar, AuthForm, ResumeUploader, JobMatchCard, AdminJobsPanel, AdminNotesPanel
│   ├── lib/                  supabase/{client,server}.ts, api.ts, useProfile.ts
│   ├── proxy.ts              route protection (Next.js 16's renamed middleware)
│   └── .env.local.example
│
├── backend/                  FastAPI (Python)
│   ├── main.py                app entry point, CORS, router registration
│   ├── app/
│   │   ├── config.py          env-driven settings
│   │   ├── database.py        Supabase client + all table/RPC access
│   │   ├── auth.py             Supabase JWT verification, get_current_user / require_admin
│   │   ├── schemas.py          Pydantic request/response models
│   │   ├── services/           resume_parser, job_search, cv_suggestions, mentor,
│   │   │                       embeddings, loader, guardrails, prompts, llm_utils
│   │   └── routers/            resumes, cv, mentor, admin
│   ├── scripts/seed_data.py   loads data/ into Supabase (jobs + career notes)
│   ├── render.yaml
│   └── .env.example
│
├── supabase/migrations/       SQL: schema, pgvector functions, RLS policies
│   ├── 0001_init.sql
│   ├── 0002_functions.sql     match_jobs(), match_career_notes()
│   └── 0003_rls.sql           Row Level Security + admin bootstrap instructions
│
├── data/                      seed content (used once by scripts/seed_data.py)
│   ├── jobs/SAMPLE_jobs.csv   86-row job corpus
│   ├── career_notes/*.txt     5-document mentor knowledge base
│   └── resumes/SAMPLE_resume.txt
│
└── legacy/                    the original Streamlit/FAISS prototype (reference only)
```

---

## 1. Set up Supabase

1. Create a project at [supabase.com](https://supabase.com).
2. Open the SQL editor and run, in order:
   - [`supabase/migrations/0001_init.sql`](supabase/migrations/0001_init.sql)
   - [`supabase/migrations/0002_functions.sql`](supabase/migrations/0002_functions.sql)
   - [`supabase/migrations/0003_rls.sql`](supabase/migrations/0003_rls.sql)
3. From **Settings → API**, note:
   - Project URL
   - `anon` `public` key (goes in the frontend)
   - `service_role` key (goes in the backend — **never** expose this to the frontend)
   - **JWT Settings → JWT Secret** (goes in the backend, used to verify tokens)

### Create your admin account

1. Run the app (or just sign up directly against Supabase Auth) and sign up
   normally with your own email/password — this creates a `profiles` row
   with `role = 'user'` automatically (via the `handle_new_user` trigger).
2. In the Supabase SQL editor, promote yourself:
   ```sql
   update public.profiles set role = 'admin' where email = 'you@example.com';
   ```
3. Sign out and back in (or just refresh) — you'll now see the **Admin** tab.

---

## 2. Run the backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
cp .env.example .env
# Fill in SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWT_SECRET, LLM_API_KEY, LLM_MODEL

uvicorn main:app --reload --port 8000
```

Verify it's up: http://localhost:8000/health

### Seed the job corpus and career notes

```bash
cd backend
python -m scripts.seed_data
```

This embeds `data/jobs/SAMPLE_jobs.csv` (86 rows) and `data/career_notes/*.txt`
(5 documents) directly into Supabase. Re-run with `--wipe` to clear and
reseed, or `--jobs-only` / `--notes-only` to seed just one corpus. You can
also add jobs and notes one at a time later from the **Admin panel** in the
running app.

---

## 3. Run the frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Fill in NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY
# NEXT_PUBLIC_API_URL defaults to http://localhost:8000

npm run dev
```

Open http://localhost:3000, sign up, and use the app. Sign in with your
promoted admin account to see the **Admin** tab.

---

## Deployment (when you're ready)

**Backend → Render:** connect the repo, set the root directory to `backend`,
and Render will pick up `backend/render.yaml` (or configure manually: build
command `pip install -r requirements.txt`, start command
`gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`).
Set the env vars from `backend/.env` as Render secrets. **Use at least the
"Standard" instance size** — `sentence-transformers` + `torch` need more
than the smallest free-tier RAM allotment to load reliably.

**Frontend → Vercel:** import the repo, set the root directory to `frontend`,
and set `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, and
`NEXT_PUBLIC_API_URL` (your Render backend's URL) as environment variables.

**CORS:** update `CORS_ORIGINS` in the backend's env to include your deployed
Vercel URL once you have it (comma-separated if you need more than one).

None of this has been connected yet — the code above is written and tested
locally, ready for you to create the actual Vercel/Render/Supabase projects
and wire the three together when you choose to.

---

## Guardrails

Every mentor question passes through `backend/app/services/guardrails.py`
before reaching the LLM:
- Empty / oversized inputs are rejected
- Unsafe topic patterns are blocked
- Output is checked for discriminatory language
- PII (email, phone) is redacted before it's stored in `chat_messages`
- The mentor's answer is checked for grounding against its retrieved sources
- Off-topic scope enforcement is handled by the mentor's system prompt (`MENTOR_SYSTEM_PROMPT`)

---

## Notes

- API keys live in `.env` files (backend) and `.env.local` (frontend), both
  gitignored — never commit real keys.
- `data/jobs/SAMPLE_jobs.csv` is an 86-row synthetic dataset structured like
  the Naukri/LinkedIn Kaggle dumps. Swap in a real dataset by replacing this
  CSV and re-running `scripts/seed_data.py --wipe --jobs-only`.
- The mentor answers from the `career_notes` table only — it says "I don't
  know" for questions outside its documents.
- `frontend/AGENTS.md` documents Next.js 16 breaking changes vs. older
  versions (e.g. `middleware.ts` → `proxy.ts`, already applied here).
