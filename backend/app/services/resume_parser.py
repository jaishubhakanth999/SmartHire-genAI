"""
Resume parsing through the central direct Sarvam client.

Responsibility: extract plain text from an uploaded resume, ask Sarvam for a
strict JSON profile, and validate that response with Pydantic before any
matching or CV feature trusts it.
"""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.services.loader import load_upload
from app.services.sarvam_client import chat_json


class Experience(BaseModel):
    title: str = Field(default="", description="Job title held.")
    company: str = Field(default="", description="Employer name.")
    start_date: Optional[str] = Field(default=None, description="Start date if stated.")
    end_date: Optional[str] = Field(default=None, description="End date if stated.")
    description: Optional[str] = Field(default=None, description="One or two lines on responsibilities or impact.")


class Education(BaseModel):
    degree: str = Field(default="", description="Degree or qualification name.")
    institution: str = Field(default="", description="School or university name.")
    year: Optional[str] = Field(default=None, description="Graduation year if stated.")


class ResumeProfile(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    target_role: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)


MAX_RESUME_TEXT_FOR_AI = 60000

_SYSTEM_PROMPT = """
You extract structured data from a resume for a job-matching application.
Return JSON only with exactly these top-level keys:
name, email, phone, target_role, skills, experience, education.
Rules:
- Use only facts explicitly present in the supplied resume text.
- Never invent employers, dates, skills, education, achievements, or contact details.
- Use null for missing scalar fields and [] for missing lists.
- Preserve the candidate's wording where useful, but keep experience descriptions concise.
- target_role may be inferred only when the resume strongly indicates it; otherwise null.
""".strip()


def parse_resume_upload(filename: str, data: bytes) -> dict:
    raw_text = load_upload(filename, data)
    ai_text = raw_text[:MAX_RESUME_TEXT_FOR_AI]

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Extract the candidate profile from this resume text. "
                f"The text may be truncated after {MAX_RESUME_TEXT_FOR_AI} characters.\n\n"
                "RESUME TEXT:\n---\n" + ai_text + "\n---"
            ),
        },
    ]

    payload = chat_json(messages, max_tokens=3500)
    profile = ResumeProfile.model_validate(payload)
    return {"parsed": profile.model_dump(), "raw_text": raw_text}


def to_search_text(parsed: dict) -> str:
    parts = [parsed.get("target_role") or "", ", ".join(parsed.get("skills", []))]
    for exp in parsed.get("experience", []):
        parts.append(f"{exp.get('title', '')} at {exp.get('company', '')}: {exp.get('description') or ''}")
    for edu in parsed.get("education", []):
        parts.append(f"{edu.get('degree', '')} - {edu.get('institution', '')}")
    return "\n".join(p for p in parts if p.strip())
