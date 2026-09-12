-- Row Level Security policies.
--
-- The backend uses the SERVICE ROLE key, which bypasses RLS entirely -- so
-- these policies are defense-in-depth for any direct client access via the
-- anon key (the frontend uses the anon key only for auth + reading its own
-- profile row; everything else goes through the backend).

alter table public.profiles enable row level security;
alter table public.resumes enable row level security;
alter table public.jobs enable row level security;
alter table public.career_notes enable row level security;
alter table public.chat_sessions enable row level security;
alter table public.chat_messages enable row level security;
alter table public.cv_suggestions enable row level security;

-- profiles: a user can read/update their own row.
create policy "profiles_select_own" on public.profiles
  for select using (auth.uid() = id);

create policy "profiles_update_own" on public.profiles
  for update using (auth.uid() = id);

-- resumes: users manage only their own.
create policy "resumes_all_own" on public.resumes
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- jobs: readable by any authenticated user; writes are backend-only (service
-- role bypasses RLS, so no direct-client write policy is defined here).
create policy "jobs_select_authenticated" on public.jobs
  for select using (auth.role() = 'authenticated');

-- career_notes: same read pattern as jobs.
create policy "career_notes_select_authenticated" on public.career_notes
  for select using (auth.role() = 'authenticated');

-- chat sessions/messages: users manage only their own.
create policy "chat_sessions_all_own" on public.chat_sessions
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "chat_messages_all_own" on public.chat_messages
  for all using (
    exists (
      select 1 from public.chat_sessions s
      where s.id = chat_messages.session_id and s.user_id = auth.uid()
    )
  )
  with check (
    exists (
      select 1 from public.chat_sessions s
      where s.id = chat_messages.session_id and s.user_id = auth.uid()
    )
  );

-- cv_suggestions: tied to resume ownership.
create policy "cv_suggestions_all_own" on public.cv_suggestions
  for all using (
    exists (
      select 1 from public.resumes r
      where r.id = cv_suggestions.resume_id and r.user_id = auth.uid()
    )
  )
  with check (
    exists (
      select 1 from public.resumes r
      where r.id = cv_suggestions.resume_id and r.user_id = auth.uid()
    )
  );

-- ---------------------------------------------------------------------------
-- Bootstrap your admin account: sign up normally in the app first, then run
-- this once in the Supabase SQL editor (runs as postgres, bypasses RLS):
--
--   update public.profiles set role = 'admin' where email = 'you@example.com';
-- ---------------------------------------------------------------------------
