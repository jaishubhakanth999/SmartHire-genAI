"""AI-first job matching through the configured Sarvam model."""

from typing import Any, Dict, List

from app.config import settings
from app.database import list_jobs
from app.services.sarvam_client import chat_json


def _catalog(jobs: List[Dict[str, Any]]) -> str:
    return "\n\n---\n\n".join(
        f"ID: {job.get('id')}\nTITLE: {job.get('title', '')}\nCOMPANY: {job.get('company', '')}\n"
        f"SKILLS: {job.get('skills', '')}\nDESCRIPTION: {job.get('description', '')}"
        for job in jobs
    )


def search_jobs(resume_search_text: str, top_k: int | None = None) -> List[Dict[str, Any]]:
    """Ask Sarvam to rank jobs for the supplied resume profile text."""
    jobs = list_jobs()
    if not jobs:
        return []

    limit = max(1, min(top_k or settings.top_k, 8))
    messages = [
        {
            "role": "system",
            "content": "You are SmartHire's job matching engine. Compare the candidate profile with the supplied jobs using semantic role alignment, skills, experience and education. Do not invent candidate facts. Return valid JSON only.",
        },
        {
            "role": "user",
            "content": (
                f"Return up to {limit} best jobs as JSON exactly in this form: "
                "{\"matches\":[{\"id\":\"existing job ID\",\"score\":0.0,\"reason\":\"brief reason\"}]} . "
                "Score must be from 0 to 1. Use only IDs from the catalog.\n\n"
                "CANDIDATE PROFILE:\n" + resume_search_text[:20000] +
                "\n\nJOB CATALOG:\n" + _catalog(jobs)[:90000]
            ),
        },
    ]
    payload = chat_json(messages, max_tokens=3000)
    raw = payload.get("matches", []) if isinstance(payload, dict) else []
    by_id = {str(job.get("id")): job for job in jobs}
    results: List[Dict[str, Any]] = []

    for item in raw:
        job_id = str(item.get("id", ""))
        job = by_id.get(job_id)
        if job is None:
            continue
        try:
            score = max(0.0, min(1.0, float(item.get("score", 0.0))))
        except (TypeError, ValueError):
            score = 0.0
        results.append({
            "id": job["id"],
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "skills": job.get("skills", ""),
            "description": job.get("description", ""),
            "similarity": score,
            "match_reason": str(item.get("reason", "")).strip(),
        })

    results.sort(key=lambda job: job["similarity"], reverse=True)
    return results[:limit]
