-- SmartHire GenAI -- initial schema
-- Run in the Supabase SQL editor, or via `supabase db push` if using the CLI.

create extension if not exists vector;
create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- Profiles: one row per auth user. Role gates admin endpoints and the
-- frontend's /admin route.
-- ---------------------------------------------------------------------------
create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  email text,
  full_name text,
  role text not null default 'user' check (role in ('user', 'admin')),
  created_at timestamptz not null default now()
);

-- Auto-create a profile row whenever someone signs up via Supabase Auth.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email, full_name)
  values (new.id, new.email, new.raw_user_meta_data ->> 'full_name');
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- ---------------------------------------------------------------------------
-- Resumes uploaded by users.
-- ---------------------------------------------------------------------------
create table if not exists public.resumes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles (id) on delete cascade,
  filename text not null,
  raw_text text,
  parsed jsonb not null,
  created_at timestamptz not null default now()
);

create index if not exists resumes_user_id_idx on public.resumes (user_id);

-- ---------------------------------------------------------------------------
-- Job postings + embeddings (the matching corpus).
-- Vector dimension must match EMBEDDING_DIMENSIONS in backend/app/config.py
-- (384 for the default sentence-transformers/all-MiniLM-L6-v2 model).
-- ---------------------------------------------------------------------------
create table if not exists public.jobs (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  company text,
  skills text,
  description text not null,
  embedding vector (384),
  created_at timestamptz not null default now()
);

create index if not exists jobs_embedding_idx
  on public.jobs using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

-- ---------------------------------------------------------------------------
-- Career notes (mentor knowledge base), chunked + embedded.
-- ---------------------------------------------------------------------------
create table if not exists public.career_notes (
  id uuid primary key default gen_random_uuid(),
  filename text not null,
  chunk_index int not null default 0,
  content text not null,
  embedding vector (384),
  created_at timestamptz not null default now()
);

create index if not exists career_notes_embedding_idx
  on public.career_notes using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

create index if not exists career_notes_filename_idx on public.career_notes (filename);

-- ---------------------------------------------------------------------------
-- Chat sessions + messages for the mentor (conversation memory).
-- ---------------------------------------------------------------------------
create table if not exists public.chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles (id) on delete cascade,
  title text,
  created_at timestamptz not null default now()
);

create index if not exists chat_sessions_user_id_idx on public.chat_sessions (user_id);

create table if not exists public.chat_messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.chat_sessions (id) on delete cascade,
  role text not null check (role in ('user', 'assistant')),
  content text not null,
  sources text[] not null default '{}',
  grounded boolean,
  blocked boolean,
  created_at timestamptz not null default now()
);

create index if not exists chat_messages_session_id_idx on public.chat_messages (session_id);

-- ---------------------------------------------------------------------------
-- CV suggestions / rewrite / explanation history (audit trail, not required
-- to be read back by the app, but useful for the admin to inspect usage).
-- ---------------------------------------------------------------------------
create table if not exists public.cv_suggestions (
  id uuid primary key default gen_random_uuid(),
  resume_id uuid not null references public.resumes (id) on delete cascade,
  job_id uuid references public.jobs (id) on delete set null,
  kind text not null check (kind in ('suggestions', 'rewrite', 'explanation')),
  content text not null,
  created_at timestamptz not null default now()
);

create index if not exists cv_suggestions_resume_id_idx on public.cv_suggestions (resume_id);
