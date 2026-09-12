"""
One-time (or re-runnable) seeding script: loads the job corpus CSV and the
career-notes documents from ../data/ into Supabase, embedding each row/chunk
along the way.

Usage (from backend/, with .venv active and backend/.env configured):
    python -m scripts.seed_data                # seed both jobs and career notes
    python -m scripts.seed_data --jobs-only
    python -m scripts.seed_data --notes-only
    python -m scripts.seed_data --wipe          # delete existing rows first

Idempotency: without --wipe, re-running appends duplicate rows if the same
CSV/notes are seeded twice. Use --wipe when re-seeding from scratch.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.database import get_client, insert_career_note_chunks, insert_job  # noqa: E402
from app.services.embeddings import embed_text, embed_texts  # noqa: E402
from app.services.loader import chunk_text  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
JOBS_CSV = DATA_DIR / "jobs" / "SAMPLE_jobs.csv"
CAREER_NOTES_DIR = DATA_DIR / "career_notes"

_TITLE_COLUMNS = ["title", "job_title", "Job Title", "position"]
_DESCRIPTION_COLUMNS = ["description", "job_description", "Job Description", "details"]
_SKILLS_COLUMNS = ["skills", "key_skills", "Key Skills", "skills_required"]
_COMPANY_COLUMNS = ["company", "company_name", "Company Name"]
_IGNORED_NAMES = {"readme.md", ".gitkeep"}


def _first_present(row: pd.Series, candidates: list[str]) -> str:
    for col in candidates:
        if col in row and pd.notna(row[col]):
            return str(row[col]).strip()
    return ""


def seed_jobs(csv_path: Path = JOBS_CSV) -> int:
    if not csv_path.exists():
        raise FileNotFoundError(f"Job dataset not found: {csv_path}")
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError(f"'{csv_path}' has no rows.")

    count = 0
    for _, row in df.iterrows():
        title = _first_present(row, _TITLE_COLUMNS)
        description = _first_present(row, _DESCRIPTION_COLUMNS)
        skills = _first_present(row, _SKILLS_COLUMNS)
        company = _first_present(row, _COMPANY_COLUMNS)

        text = "\n".join(
            part
            for part in [f"Title: {title}" if title else "", f"Skills: {skills}" if skills else "", description]
            if part
        ).strip()
        if not text:
            continue

        embedding = embed_text(text)
        insert_job(title, company, skills, description, embedding)
        count += 1
        print(f"  [{count}] {title} @ {company or '-'}")
    return count


def seed_career_notes(notes_dir: Path = CAREER_NOTES_DIR) -> int:
    if not notes_dir.exists():
        raise FileNotFoundError(f"Career notes directory not found: {notes_dir}")

    total_chunks = 0
    for path in sorted(notes_dir.iterdir()):
        if not path.is_file() or path.name.lower() in _IGNORED_NAMES or path.suffix.lower() != ".txt":
            continue
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            continue
        chunks = chunk_text(text, chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
        embeddings = embed_texts(chunks)
        rows = [
            {"filename": path.name, "chunk_index": i, "content": c, "embedding": e}
            for i, (c, e) in enumerate(zip(chunks, embeddings))
        ]
        insert_career_note_chunks(rows)
        total_chunks += len(rows)
        print(f"  {path.name}: {len(rows)} chunk(s)")
    return total_chunks


def wipe():
    client = get_client()
    client.table("jobs").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    client.table("career_notes").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    print("Wiped existing jobs and career_notes rows.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs-only", action="store_true")
    parser.add_argument("--notes-only", action="store_true")
    parser.add_argument("--wipe", action="store_true", help="Delete existing jobs/career_notes rows first.")
    args = parser.parse_args()

    settings.require_supabase()

    if args.wipe:
        wipe()

    if not args.notes_only:
        print("Seeding jobs...")
        n = seed_jobs()
        print(f"Seeded {n} job(s).\n")

    if not args.jobs_only:
        print("Seeding career notes...")
        n = seed_career_notes()
        print(f"Seeded {n} career-note chunk(s).")
