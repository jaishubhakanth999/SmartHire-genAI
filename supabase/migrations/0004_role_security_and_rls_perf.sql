-- Security and performance hardening for direct client RLS access.
-- Admin authorization depends on profiles.role, so clients must never be able
-- to update that column through the anon key.

drop policy if exists "profiles_update_own" on public.profiles;

drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own" on public.profiles
  for select
  to authenticated
  using ((select auth.uid()) = id);

-- Users do not update profiles directly. Profile role remains backend/admin controlled.

drop policy if exists "resumes_all_own" on public.resumes;
create policy "resumes_all_own" on public.resumes
  for all
  to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "jobs_select_authenticated" on public.jobs;
create policy "jobs_select_authenticated" on public.jobs
  for select
  to authenticated
  using ((select auth.uid()) is not null);

drop policy if exists "career_notes_select_authenticated" on public.career_notes;
create policy "career_notes_select_authenticated" on public.career_notes
  for select
  to authenticated
  using ((select auth.uid()) is not null);

drop policy if exists "chat_sessions_all_own" on public.chat_sessions;
create policy "chat_sessions_all_own" on public.chat_sessions
  for all
  to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "chat_messages_all_own" on public.chat_messages;
create policy "chat_messages_all_own" on public.chat_messages
  for all
  to authenticated
  using (
    exists (
      select 1
      from public.chat_sessions s
      where s.id = chat_messages.session_id
        and s.user_id = (select auth.uid())
    )
  )
  with check (
    exists (
      select 1
      from public.chat_sessions s
      where s.id = chat_messages.session_id
        and s.user_id = (select auth.uid())
    )
  );

drop policy if exists "cv_suggestions_all_own" on public.cv_suggestions;
create policy "cv_suggestions_all_own" on public.cv_suggestions
  for all
  to authenticated
  using (
    exists (
      select 1
      from public.resumes r
      where r.id = cv_suggestions.resume_id
        and r.user_id = (select auth.uid())
    )
  )
  with check (
    exists (
      select 1
      from public.resumes r
      where r.id = cv_suggestions.resume_id
        and r.user_id = (select auth.uid())
    )
  );
