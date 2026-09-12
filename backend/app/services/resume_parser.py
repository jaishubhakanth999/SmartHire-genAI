"""
Resume parsing.

Responsibility: turn raw resume text into a clean, structured profile --
name, contact info, skills, experience, education, target role -- using the
LLM's structured-output mode, validated with Pydantic before anything
downstream trusts it.
"""

from typing import List, Optional

from langchain_sarvam import ChatSarvam
from pydantic import BaseModel, Field, ValidationError

from app.config import settings
from app.services.loader import load_upload
from app.services.prompts import RESUME_PARSE_PROMPT


class Experience(BaseModel):
    title: str = Field(description="Job title held.")
    company: str = Field(description="Employer name.")
    start_date: Optional[str] = Field(default=None, description="e.g. 'Jan 2022' or 'unknown'.")
    end_date: Optional[str] = Field(default=None, description="e.g. 'Present' or 'unknown'.")
    description: Optional[str] = Field(default=None, description="One or two lines on responsibilities/impact.")


class Education(BaseModel):
    degree: str = Field(description="Degree or qualification name.")
    institution: str = Field(description="School / university name.")
    year: Optional[str] = Field(default=None, description="Graduation year, if stated.")


class ResumeProfile(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    target_role: Optional[str] = Field(default=None, description="Role the candidate appears to target.")
    skills: List[str] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)


_llm: Optional[ChatSarvam] = None
_MAX_ATTEMPTS = 3


def get_llm() -> ChatSarvam:
    global _llm
    if _llm is None:
        settings.require_llm()
        # max_tokens is generous on purpose -- see the comment in
        # app/services/cv_suggestions.py's get_llm() for why.
        _llm = ChatSarvam(model=settings.llm_model, api_key=settings.llm_api_key, temperature=0, max_tokens=4096)
    return _llm


def parse_resume_upload(filename: str, data: bytes) -> dict:
    """
    Load an uploaded resume file's bytes and return a structured, validated
    profile (dict) plus the raw extracted text.

    Raises:
        ValueError: if the file can't be read, or every attempt's LLM output
            fails Pydantic validation.
    """
    raw_text = load_upload(filename, data)
    structured_llm = get_llm().with_structured_output(ResumeProfile)

    profile: Optional[ResumeProfile] = None
    last_error: Optional[Exception] = None
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            result = structured_llm.invoke(RESUME_PARSE_PROMPT.format(resume_text=raw_text))
            profile = result if isinstance(result, ResumeProfile) else ResumeProfile.model_validate(result)
            break
        except Exception as exc:  # network/API errors and validation errors alike
            last_error = exc
            if attempt == _MAX_ATTEMPTS:
                raise ValueError(f"Resume parsing failed after {_MAX_ATTEMPTS} attempts: {exc}") from exc

    assert profile is not None  # loop either sets profile or raises
    return {"parsed": profile.model_dump(), "raw_text": raw_text}


def to_search_text(parsed: dict) -> str:
    """Flatten a structured resume into the single string used for job matching."""
    parts = [parsed.get("target_role") or "", ", ".join(parsed.get("skills", []))]
    for exp in parsed.get("experience", []):
        parts.append(f"{exp.get('title', '')} at {exp.get('company', '')}: {exp.get('description') or ''}")
    for edu in parsed.get("education", []):
        parts.append(f"{edu.get('degree', '')} - {edu.get('institution', '')}")
    return "\n".join(p for p in parts if p.strip())
