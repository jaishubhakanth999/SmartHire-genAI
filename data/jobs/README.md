# data/jobs/

Job descriptions that seed the **matching corpus** in Supabase.

`SAMPLE_jobs.csv` is an 86-row synthetic dataset spanning tech, data,
product, design, sales, marketing, HR, finance and operations roles,
structured the same way as the Naukri/LinkedIn Kaggle dumps referenced in
the original project spec (title, company, skills, description columns).

- Loaded once by `backend/scripts/seed_data.py`, which embeds each row and
  inserts it into the Supabase `jobs` table (see `supabase/migrations/0001_init.sql`).
- After seeding, jobs live in Postgres, not in this file — this CSV is only
  the seed source. Add/remove jobs afterward from the **Admin panel** in the
  running app, or re-run the seed script.
- To swap in a real Kaggle dataset: replace this CSV (same column names, or
  edit the `_TITLE_COLUMNS`/etc. lists in `backend/scripts/seed_data.py` to
  match a different dump's headers), then run:
  ```bash
  cd backend
  python -m scripts.seed_data --wipe --jobs-only
  ```
