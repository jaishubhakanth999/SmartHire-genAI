"""Direct Sarvam CV coaching actions."""

import json

from app.services.sarvam_client import chat


def _resume_json(parsed: dict) -> str:
    return json.dumps(parsed, default=str, ensure_ascii=False)


def _job_text(job: dict) -> str:
    return f"Title: {job.get('title', '')}\nDescription: {job.get('description', '')}\nSkills: {job.get('skills', '')}"


def suggest_improvements(parsed_resume: dict, job: dict) -> str:
    messages = [
        {"role": "system", "content": "You are a practical CV coach. Use only facts in the supplied candidate profile. Never invent experience, employers, skills, dates or achievements."},
        {"role": "user", "content": f"CANDIDATE PROFILE:\n{_resume_json(parsed_resume)}\n\nTARGET JOB:\n{_job_text(job)}\n\nGive: (1) missing or weakly evidenced skills, (2) 2-3 stronger rewrites of existing experience bullets using only supplied facts, and (3) a targeted 2-3 sentence summary."},
    ]
    return chat(messages, max_tokens=2500)


def explain_match(parsed_resume: dict, job: dict) -> str:
    messages = [
        {"role": "system", "content": "Explain a resume-to-job match using only the supplied facts. Do not invent overlap."},
        {"role": "user", "content": f"CANDIDATE PROFILE:\n{_resume_json(parsed_resume)}\n\nJOB:\n{_job_text(job)}\n\nExplain in 3-5 clear bullet points why this role fits, and mention important gaps."},
    ]
    return chat(messages, max_tokens=1600)


def rewrite_resume_for_job(parsed_resume: dict, job: dict) -> str:
    messages = [
        {"role": "system", "content": "Rewrite resume content for the target job using ONLY facts already present in the candidate profile. Never fabricate facts or achievements."},
        {"role": "user", "content": f"CANDIDATE PROFILE:\n{_resume_json(parsed_resume)}\n\nJOB:\n{_job_text(job)}\n\nProduce: PROFESSIONAL SUMMARY, SKILLS, EXPERIENCE. Keep every employer, date, skill and achievement grounded in the supplied profile."},
    ]
    return chat(messages, max_tokens=3000)
