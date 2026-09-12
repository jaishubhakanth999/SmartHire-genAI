-- Vector similarity search RPCs, called from the backend via
-- supabase-py's `.rpc("match_jobs", ...)` / `.rpc("match_career_notes", ...)`.

create or replace function public.match_jobs(
  query_embedding vector (384),
  match_count int default 5
)
returns table (
  id uuid,
  title text,
  company text,
  skills text,
  description text,
  similarity float
)
language sql
stable
as $$
  select
    id,
    title,
    company,
    skills,
    description,
    1 - (embedding <=> query_embedding) as similarity
  from public.jobs
  where embedding is not null
  order by embedding <=> query_embedding
  limit match_count;
$$;

create or replace function public.match_career_notes(
  query_embedding vector (384),
  match_count int default 5
)
returns table (
  id uuid,
  filename text,
  content text,
  similarity float
)
language sql
stable
as $$
  select
    id,
    filename,
    content,
    1 - (embedding <=> query_embedding) as similarity
  from public.career_notes
  where embedding is not null
  order by embedding <=> query_embedding
  limit match_count;
$$;
