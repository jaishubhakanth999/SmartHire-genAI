"""
Resume-to-job matching (Module 2 of the spec).

Responsibility: the matching feature. Load the job dataset (CSV) into
documents, build/query the FAISS index via embed.py, rank results for a
candidate resume, and return scored job matches with simple, explainable
matched/missing-skill breakdowns.

Depends on embed.py for the vector layer; knows nothing about how vectors
are stored.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from src.config import load_config
from src.search.embed import build_index, index_exists, load_index

PathLike = Union[str, Path]

# The Kaggle Naukri/LinkedIn dumps referenced in the spec use varying column
# names -- try a short list of likely candidates for each field so the same
# code works whichever dump you download.
_TITLE_COLUMNS = ["title", "job_title", "Job Title", "position"]
_DESCRIPTION_COLUMNS = ["description", "job_description", "Job Description", "details"]
_SKILLS_COLUMNS = ["skills", "key_skills", "Key Skills", "skills_required"]
_COMPANY_COLUMNS = ["company", "company_name", "Company Name"]


def _first_present(row: pd.Series, candidates: List[str]) -> str:
    for col in candidates:
        if col in row and pd.notna(row[col]):
            return str(row[col]).strip()
    return ""


def load_job_dataset(csv_path: PathLike) -> List[Dict[str, Any]]:
    """
    Load a job-postings CSV into {"text", "metadata"} documents ready for
    embed.build_index(). Tolerant of the differing column names used by
    different Kaggle Naukri/LinkedIn dumps (see the *_COLUMNS lists above).

    Raises:
        ValueError: if the CSV has no rows, or no row yields any usable text
            (title/description/skills all blank) -- that almost always means
            the column-name guesses above need a row added for this dataset.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Job dataset not found: {csv_path}")

    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError(f"'{csv_path}' has no rows.")

    documents: List[Dict[str, Any]] = []
    for i, row in df.iterrows():
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

        documents.append(
            {
                "text": text,
                "metadata": {
                    "job_id": str(row.get("job_id", i)),
                    "title": title,
                    "company": company,
                    "skills": skills,
                    "source": str(csv_path),
                },
            }
        )

    if not documents:
        raise ValueError(
            f"No usable rows found in '{csv_path}'. Expected one of these column "
            f"names for the title: {_TITLE_COLUMNS} -- check the CSV's real headers "
            "and add the right one to job_search.py's *_COLUMNS lists."
        )
    return documents


def build_job_index(csv_path: Optional[PathLike] = None, persist_dir: Optional[PathLike] = None):
    """Load the job dataset and (re)build its FAISS index. Returns the index."""
    config = load_config()
    csv_path = Path(csv_path) if csv_path else _default_csv_path(config)
    persist_dir = Path(persist_dir) if persist_dir else (config.vectorstore_dir / "jobs")
    documents = load_job_dataset(csv_path)
    return build_index(documents, persist_dir)


def _default_csv_path(config) -> Path:
    csv_files = sorted(config.jobs_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files in '{config.jobs_dir}'. Put the job dataset there "
            "(see data/jobs/README.md), or pass csv_path explicitly."
        )
    return csv_files[0]


def search_jobs(resume_text: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Return the top-k jobs most similar to a resume's search text.

    Each result is {"title", "company", "skills", "description", "score"},
    where `score` is a 0-1 similarity (higher is better; FAISS's raw L2
    distance is converted so results read naturally).
    """
    config = load_config()
    persist_dir = config.vectorstore_dir / "jobs"
    if not index_exists(persist_dir):
        raise FileNotFoundError(
            "No job index found. Build it first: "
            "python -m src.search.job_search --build"
        )
    index = load_index(persist_dir)
    k = top_k or config.top_k

    results = []
    for doc, distance in index.similarity_search_with_score(resume_text, k=k):
        score = 1.0 / (1.0 + distance)  # monotonic decreasing distance -> increasing score in (0, 1]
        results.append(
            {
                "title": doc.metadata.get("title", ""),
                "company": doc.metadata.get("company", ""),
                "skills": doc.metadata.get("skills", ""),
                "description": doc.page_content,
                "score": round(score, 4),
            }
        )
    return results


def score_match(resume: dict, job: dict) -> float:
    """Produce a 0-1 skill-overlap score for one resume/job pair (deterministic, no LLM call)."""
    resume_skills = {s.strip().lower() for s in resume.get("skills", []) if s.strip()}
    job_skills = _job_skill_set(job)
    if not job_skills:
        return 0.0
    return round(len(resume_skills & job_skills) / len(job_skills), 4)


def matched_skills(resume: dict, job: dict) -> List[str]:
    """Return skills present in both the resume and the job description."""
    resume_skills = {s.strip().lower(): s.strip() for s in resume.get("skills", []) if s.strip()}
    job_skills = _job_skill_set(job)
    return [resume_skills[s] for s in job_skills if s in resume_skills]


def missing_skills(resume: dict, job: dict) -> List[str]:
    """Return skills the job asks for that the resume does not evidence."""
    resume_skills = {s.strip().lower() for s in resume.get("skills", []) if s.strip()}
    job_skills_raw = [s.strip() for s in job.get("skills", "").split(",") if s.strip()]
    return [s for s in job_skills_raw if s.lower() not in resume_skills]


def _job_skill_set(job: dict) -> set:
    return {s.strip().lower() for s in job.get("skills", "").split(",") if s.strip()}


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Build or query the job FAISS index.")
    parser.add_argument("--build", action="store_true", help="(Re)build the job index from data/jobs/*.csv")
    parser.add_argument("--query", type=str, default=None, help="Resume text to search jobs for")
    args = parser.parse_args()

    if args.build:
        idx = build_job_index()
        print(f"Job index built with {idx.index.ntotal} vector(s).")
    if args.query:
        for r in search_jobs(args.query):
            print(json.dumps(r, indent=2))
